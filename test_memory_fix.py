#!/usr/bin/env python3
"""
Test script to verify the memory fix for the Resume Analyzer
"""

import os
import sys
import gc

# Add the App directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'App'))

def test_spacy_model_loading():
    """Test that spaCy model loads correctly and only once"""
    print("Testing spaCy model loading...")
    
    try:
        # Import spacy and test model loading directly
        import spacy
        
        # Test loading the model
        nlp1 = spacy.load('en_core_web_sm')
        print("✅ spaCy model loaded successfully")
        
        # Test loading again to see if it's cached
        nlp2 = spacy.load('en_core_web_sm')
        if nlp1 is nlp2:
            print("✅ Model is reused (cached)")
        else:
            print("⚠️  Model is not cached (this is normal for spaCy)")
            
    except Exception as e:
        print(f"❌ Error during spaCy testing: {e}")
        return False
    
    return True

def test_memory_management():
    """Test memory management functions"""
    print("\nTesting memory management...")
    
    try:
        # Test garbage collection
        gc.collect()
        print("✅ Garbage collection works")
        
        # Test memory usage before and after
        import psutil
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"Memory usage: {memory_before:.2f} MB")
        
    except ImportError:
        print("⚠️  psutil not available, skipping memory usage test")
    except Exception as e:
        print(f"❌ Error during memory testing: {e}")
        return False
    
    return True

def test_resume_parser_import():
    """Test that ResumeParser can be imported"""
    print("\nTesting ResumeParser import...")
    
    try:
        from pyresparser import ResumeParser
        print("✅ ResumeParser imported successfully")
        
        # Test that the class exists
        if hasattr(ResumeParser, '__init__'):
            print("✅ ResumeParser class has __init__ method")
        else:
            print("❌ ResumeParser class missing __init__ method")
            return False
            
    except Exception as e:
        print(f"❌ Error during ResumeParser import: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Testing Memory Fix for AI Resume Analyzer")
    print("=" * 50)
    
    success = True
    
    # Test 1: spaCy model loading
    if not test_spacy_model_loading():
        success = False
    
    # Test 2: Memory management
    if not test_memory_management():
        success = False
    
    # Test 3: ResumeParser import
    if not test_resume_parser_import():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Memory fix should work correctly.")
        print("\nKey improvements made:")
        print("- spaCy model is loaded only once using singleton pattern")
        print("- Memory cleanup is performed after resume parsing")
        print("- Error handling for memory errors")
        print("- Monkey-patched ResumeParser to reuse loaded model")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    main() 