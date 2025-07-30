# Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
import spacy
import gc
from spacy.matcher import Matcher
# Import the improved resume scorer
# from resume_scorer import ResumeScorer
# Import the improved resume analysis
# from improved_resume_analysis import display_improved_resume_analysis

# Import job recommendation module
from job_recommendation import get_global_jobs, get_nepal_jobs


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='',db='cv')
cursor = connection.cursor()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
)


###### Main function run() ######


def run():
    
    # (Logo, Heading, Sidebar etc)
    img = Image.open('./Logo/Resume.png')
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin", "Job Recommendations"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                
                # Safe string concatenation with null checks
                name = resume_data.get('name', 'User')
                if name is None:
                    name = 'User'
                st.success("Hello " + name)
                
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: ' + (resume_data.get('name', 'Not found') or 'Not found'))
                    st.text('Email: ' + (resume_data.get('email', 'Not found') or 'Not found'))
                    st.text('Contact: ' + (resume_data.get('mobile_number', 'Not found') or 'Not found'))
                    st.text('Degree: ' + str(resume_data.get('degree', 'Not found') or 'Not found'))
                    st.text('Resume pages: ' + str(resume_data.get('no_of_pages', 0) or 0))

                except Exception as e:
                    st.error(f"Error displaying basic info: {str(e)}")
                    st.text('Name: Not found')
                    st.text('Email: Not found')
                    st.text('Contact: Not found')
                    st.text('Degree: Not found')
                    st.text('Resume pages: 0')
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                safe_pages = resume_data.get('no_of_pages', 0) or 0
                if safe_pages < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                # Safe handling of skills data
                skills = resume_data.get('skills', [])
                if skills is None:
                    skills = []
                
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=skills,key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                for i in skills:
                
                    #### Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ds_course)
                        break

                    #### Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(web_course)
                        break

                    #### Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(android_course)
                        break

                    #### IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(ios_course)
                        break

                    #### Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = course_recommender(uiux_course)
                        break

                    #### For Not Any Recommendations
                    elif i.lower() in n_any:
                        print(i.lower())
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Currently No Recommendations',value=recommended_skills,key = '6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                        # course recommendation
                        rec_course = "Sorry! Not Available for this Field"
                        break


                ## Improved Resume Analysis & Scoring
                st.subheader("**Improved Resume Analysis & Scoring 🎯**")
                
                # Enhanced basic scoring with better analysis
                resume_score = 0
                
                # Check for key sections with improved scoring
                if 'Objective' in resume_text or 'Summary' in resume_text:
                    resume_score += 8
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added Objective/Summary</h4>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intention to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Education' in resume_text or 'School' in resume_text or 'College' in resume_text:
                    resume_score += 15
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Great! You have added Education Details</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text or 'Experience' in resume_text:
                    resume_score += 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added Experience</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'INTERNSHIPS' in resume_text or 'INTERNSHIP' in resume_text or 'Internships' in resume_text or 'Internship' in resume_text:
                    resume_score += 8
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Great! You have added Internships</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                if 'SKILLS' in resume_text or 'SKILL' in resume_text or 'Skills' in resume_text or 'Skill' in resume_text:
                    resume_score += 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added Skills</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text or 'Hobbies' in resume_text:
                    resume_score += 5
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters</h4>''',unsafe_allow_html=True)

                if 'INTERESTS' in resume_text or 'Interests' in resume_text:
                    resume_score += 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have added your Interest</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other than job.</h4>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text or 'Achievements' in resume_text:
                    resume_score += 15
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added your Achievements</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text or 'Certifications' in resume_text or 'Certification' in resume_text:
                    resume_score += 12
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Great! You have added your Certifications</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text or 'PROJECT' in resume_text or 'Projects' in resume_text or 'Project' in resume_text:
                    resume_score += 18
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related to the required position.</h4>''',unsafe_allow_html=True)

                # Additional analysis for better scoring
                # Check for action verbs
                action_verbs = ['developed', 'implemented', 'designed', 'created', 'built', 'launched', 'managed', 'led', 'coordinated', 'optimized', 'improved', 'increased', 'decreased', 'reduced', 'enhanced', 'streamlined', 'automated', 'deployed', 'maintained', 'analyzed', 'researched', 'collaborated', 'mentored', 'delivered', 'achieved', 'exceeded', 'generated', 'saved', 'boosted']
                action_verbs_found = [verb for verb in action_verbs if verb in resume_text.lower()]
                if len(action_verbs_found) >= 3:
                    resume_score += 8
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You are using strong action verbs</h4>''',unsafe_allow_html=True)
                elif len(action_verbs_found) >= 1:
                    resume_score += 4
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You are using some action verbs</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Try to use more action verbs like 'Developed', 'Implemented', 'Led', 'Achieved'</h4>''',unsafe_allow_html=True)

                # Check for quantifiable achievements
                import re
                numbers_pattern = r'\b\d+(?:\.\d+)?%?\b'
                numbers_found = re.findall(numbers_pattern, resume_text)
                if len(numbers_found) >= 2:
                    resume_score += 6
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Great! You have quantifiable achievements</h4>''',unsafe_allow_html=True)
                elif len(numbers_found) >= 1:
                    resume_score += 3
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have some quantifiable achievements</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Try to include specific metrics and numbers to demonstrate your impact</h4>''',unsafe_allow_html=True)

                # Check for contact information
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
                
                if re.search(email_pattern, resume_text):
                    resume_score += 3
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have included email</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your email address</h4>''',unsafe_allow_html=True)
                
                if re.search(phone_pattern, resume_text):
                    resume_score += 3
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have included phone number</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your phone number</h4>''',unsafe_allow_html=True)

                # Display overall score with grade
                st.subheader("**Resume Score Summary 📊**")
                
                # Calculate grade
                if resume_score >= 90:
                    grade = 'A+'
                    grade_description = 'Excellent'
                elif resume_score >= 80:
                    grade = 'A'
                    grade_description = 'Very Good'
                elif resume_score >= 70:
                    grade = 'B+'
                    grade_description = 'Good'
                elif resume_score >= 60:
                    grade = 'B'
                    grade_description = 'Above Average'
                elif resume_score >= 50:
                    grade = 'C+'
                    grade_description = 'Average'
                else:
                    grade = 'C'
                    grade_description = 'Needs Improvement'
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Score", f"{resume_score}/100")
                with col2:
                    st.metric("Grade", grade)
                with col3:
                    st.metric("Status", grade_description)
                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated using improved analysis of your resume content, structure, and professional presentation. **")

                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data
                # Safe data extraction with null checks
                safe_name = resume_data.get('name', 'Unknown') or 'Unknown'
                safe_email = resume_data.get('email', 'Unknown') or 'Unknown'
                safe_pages = resume_data.get('no_of_pages', 0) or 0
                safe_skills = resume_data.get('skills', []) or []
                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), safe_name, safe_email, str(resume_score), timestamp, str(safe_pages), reco_field, cand_level, str(safe_skills), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## Job Recommendations
                st.subheader("**Job Recommendations 💼**")

                with st.spinner('Fetching job recommendations...'):

                    # Use only the most relevant and broad skills for job search
                    skills = resume_data.get('skills', [])
                    # Use only the first 3 skills, and filter out very specific/rare ones (length > 2)
                    filtered_skills = [s for s in skills if len(s.strip()) > 2][:3]
                    
                    # If no skills found, use the predicted field
                    if not filtered_skills and reco_field:
                        filtered_skills = [reco_field.lower()]
                    
                    # Add broad fallback queries
                    broad_queries = ["developer", "engineer", "software", "IT", "technology"]
                    queries = list(set(filtered_skills + broad_queries))

                    # Get job recommendations using the improved system
                    from job_recommendation import get_global_jobs, get_nepal_jobs
                    
                    combined_jobs = []
                    seen_titles = set()

                    # Try to get jobs for each query
                    for query in queries[:3]:  # Limit to 3 queries to avoid too many requests
                        try:
                            # Get global jobs
                            global_jobs = get_global_jobs(query=query)
                            for job in global_jobs:
                                if job['title'] not in seen_titles:
                                    combined_jobs.append(job)
                                    seen_titles.add(job['title'])
                            
                            # Get Nepal-specific jobs
                            nepal_jobs = get_nepal_jobs(query=query)
                            for job in nepal_jobs:
                                if job['title'] not in seen_titles:
                                    combined_jobs.append(job)
                                    seen_titles.add(job['title'])
                                    
                        except Exception as e:
                            st.warning(f"Could not fetch jobs for '{query}': {str(e)}")
                            continue

                    # Filter for Data Scientist jobs only
                    # Determine the main job type by resume name/title
                    main_job_title = resume_data.get('name', '').strip().lower() if resume_data.get('name') else ''
                    if main_job_title == 'data scientist':
                        filtered_jobs = [job for job in combined_jobs if "data scientist" in job['title'].lower()]
                        upwork_job = {
                            'title': 'Data Scientist (Freelance Opportunities)',
                            'company': 'Upwork',
                            'location': 'Remote',
                            'link': 'https://www.upwork.com/freelance-jobs/data-science/',
                            'description': 'Browse and apply for freelance Data Science jobs on Upwork.'
                        }
                        linkedin_job = {
                            'title': 'Data Scientist (Global Opportunities)',
                            'company': 'LinkedIn',
                            'location': 'Worldwide',
                            'link': 'https://www.linkedin.com/jobs/data-scientist-jobs-worldwide/?currentJobId=4276624868',
                            'description': 'Explore Data Scientist jobs worldwide on LinkedIn.'
                        }
                        indeed_job = {
                            'title': 'International Machine Learning/Data Scientist Jobs',
                            'company': 'Indeed',
                            'location': 'International',
                            'link': 'https://www.indeed.com/q-international-machine-learning-jobs.html?vjk=f36a29550efb26ad',
                            'description': 'Find international Machine Learning and Data Scientist jobs on Indeed.'
                        }
                        filtered_jobs = [upwork_job, linkedin_job, indeed_job] + filtered_jobs
                        if filtered_jobs:
                            st.success(f"Found {len(filtered_jobs)} Data Scientist job recommendations!")
                            for i, job in enumerate(filtered_jobs, 1):
                                with st.container():
                                    st.markdown(f"### {i}. [{job['title']}]({job['link']})")
                                    st.markdown(f"**🏢 Company:** {job['company']}")
                                    st.markdown(f"**📍 Location:** {job.get('location', 'N/A')}")
                                    if 'description' in job:
                                        st.markdown(f"**📝 Description:** {job['description']}")
                                    st.markdown("---")
                            st.info("💡 **Note:** Only Data Scientist jobs are shown based on your resume and real-time data. Always verify job details before applying.")
                        else:
                            st.warning("No Data Scientist job recommendations found at the moment.")
                            st.info("💡 **Tip:** Try uploading a resume with more specific data science skills to get better job matches.")
                    elif main_job_title == 'android developer':
                        filtered_jobs = [job for job in combined_jobs if "android developer" in job['title'].lower()]
                        linkedin_job = {
                            'title': 'Android Developer (Global Opportunities)',
                            'company': 'LinkedIn',
                            'location': 'Worldwide',
                            'link': 'https://www.linkedin.com/jobs/android-developer-jobs-worldwide/?currentJobId=4276548138',
                            'description': 'Explore Android Developer jobs worldwide on LinkedIn.'
                        }
                        indeed_job = {
                            'title': 'International Remote Android Developer Jobs',
                            'company': 'Indeed',
                            'location': 'International/Remote',
                            'link': 'https://www.indeed.com/q-international-remote-android-developer-jobs.html?vjk=7d6e95a45d8f0d13',
                            'description': 'Find international remote Android Developer jobs on Indeed.'
                        }
                        ziprecruiter_job = {
                            'title': 'International Android Developer Jobs',
                            'company': 'ZipRecruiter',
                            'location': 'International',
                            'link': 'https://www.ziprecruiter.com/Jobs/International-Android-Developer',
                            'description': 'Browse international Android Developer jobs on ZipRecruiter.'
                        }
                        filtered_jobs = [linkedin_job, indeed_job, ziprecruiter_job] + filtered_jobs
                        if filtered_jobs:
                            st.success(f"Found {len(filtered_jobs)} Android Developer job recommendations!")
                            for i, job in enumerate(filtered_jobs, 1):
                                with st.container():
                                    st.markdown(f"### {i}. [{job['title']}]({job['link']})")
                                    st.markdown(f"**🏢 Company:** {job['company']}")
                                    st.markdown(f"**📍 Location:** {job.get('location', 'N/A')}")
                                    if 'description' in job:
                                        st.markdown(f"**📝 Description:** {job['description']}")
                                    st.markdown("---")
                            st.info("💡 **Note:** Only Android Developer jobs are shown based on your resume and real-time data. Always verify job details before applying.")
                        else:
                            st.warning("No Android Developer job recommendations found at the moment.")
                            st.info("💡 **Tip:** Try uploading a resume with more specific Android skills to get better job matches.")
                    else:
                        # Default: show jobs matching the queries, but do not inject special links
                        if combined_jobs:
                            st.success(f"Found {len(combined_jobs)} job recommendations!")
                            for i, job in enumerate(combined_jobs, 1):
                                with st.container():
                                    st.markdown(f"### {i}. [{job['title']}]({job['link']})")
                                    st.markdown(f"**🏢 Company:** {job['company']}")
                                    st.markdown(f"**📍 Location:** {job.get('location', 'N/A')}")
                                    if 'description' in job:
                                        st.markdown(f"**📝 Description:** {job['description']}")
                                    st.markdown("---")
                            st.info("💡 **Note:** Jobs are shown based on your resume and real-time data. Always verify job details before applying.")
                        else:
                            st.warning("No job recommendations found at the moment.")
                            st.info("💡 **Tip:** Try uploading a resume with more specific skills to get better job matches.")

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
        </p><br/><br/>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Admin ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()

# Global variable to store the spaCy model
_nlp_model = None

def get_spacy_model():
    """Get or load spaCy model to prevent memory issues"""
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load('en_core_web_sm')
        except OSError:
            st.error("spaCy model 'en_core_web_sm' not found. Please install it using: python -m spacy download en_core_web_sm")
            return None
    return _nlp_model

def cleanup_memory():
    """Force garbage collection to free up memory"""
    gc.collect()

# Monkey patch the ResumeParser to use pre-loaded model
original_init = ResumeParser.__init__

def patched_init(self, resume, skills_file=None, custom_regex=None):
    nlp = get_spacy_model()
    if nlp is None:
        raise RuntimeError("spaCy model not loaded")
    # Use only the preloaded model for both nlp and custom_nlp
    custom_nlp = nlp
    from pyresparser import utils
    from spacy.matcher import Matcher
    import io
    import os
    # Use name-mangled attributes to match the original ResumeParser
    self._ResumeParser__skills_file = skills_file
    self._ResumeParser__custom_regex = custom_regex
    self._ResumeParser__matcher = Matcher(nlp.vocab)
    self._ResumeParser__details = {
        'name': None,
        'email': None,
        'mobile_number': None,
        'skills': None,
        'degree': None,
        'no_of_pages': None,
    }
    self._ResumeParser__resume = resume
    if not isinstance(self._ResumeParser__resume, io.BytesIO):
        ext = os.path.splitext(self._ResumeParser__resume)[1].split('.')[1]
    else:
        ext = self._ResumeParser__resume.name.split('.')[1]
    self._ResumeParser__text_raw = utils.extract_text(self._ResumeParser__resume, '.' + ext)
    self._ResumeParser__text = ' '.join(self._ResumeParser__text_raw.split())
    self._ResumeParser__nlp = nlp(self._ResumeParser__text)
    self._ResumeParser__custom_nlp = custom_nlp(self._ResumeParser__text_raw)
    self._ResumeParser__noun_chunks = list(self._ResumeParser__nlp.noun_chunks)
    # Inline logic from __get_basic_details
    cust_ent = utils.extract_entities_wih_custom_model(self._ResumeParser__custom_nlp)
    name = utils.extract_name(self._ResumeParser__nlp, matcher=self._ResumeParser__matcher)
    email = utils.extract_email(self._ResumeParser__text)
    mobile = utils.extract_mobile_number(self._ResumeParser__text, self._ResumeParser__custom_regex)
    skills = utils.extract_skills(self._ResumeParser__nlp, self._ResumeParser__noun_chunks, self._ResumeParser__skills_file)
    entities = utils.extract_entity_sections_grad(self._ResumeParser__text_raw)
    try:
        self._ResumeParser__details['name'] = cust_ent['Name'][0]
    except (IndexError, KeyError):
        self._ResumeParser__details['name'] = name
    self._ResumeParser__details['email'] = email
    self._ResumeParser__details['mobile_number'] = mobile
    self._ResumeParser__details['skills'] = skills
    self._ResumeParser__details['no_of_pages'] = utils.get_number_of_pages(self._ResumeParser__resume)
    try:
        self._ResumeParser__details['degree'] = cust_ent['Degree']
    except KeyError:
        pass

# Apply the patch
ResumeParser.__init__ = patched_init
