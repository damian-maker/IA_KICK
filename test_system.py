"""
System test and validation script
Tests all components and verifies installation
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version OK")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print_header("Checking FFmpeg")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(version_line)
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg not working properly")
            return False
            
    except FileNotFoundError:
        print("❌ FFmpeg not found in PATH")
        print("Please install FFmpeg from: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False


def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        'gradio',
        'numpy',
        'pandas',
        'cv2',
        'librosa',
        'sklearn',
        'requests',
        'ffmpeg',
        'yt_dlp'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                __import__('cv2')
                package_name = 'opencv-python'
            elif package == 'sklearn':
                __import__('sklearn')
                package_name = 'scikit-learn'
            elif package == 'ffmpeg':
                __import__('ffmpeg')
                package_name = 'ffmpeg-python'
            elif package == 'yt_dlp':
                __import__('yt_dlp')
                package_name = 'yt-dlp'
            else:
                __import__(package)
                package_name = package
            
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_directories():
    """Check if required directories exist"""
    print_header("Checking Directories")
    
    dirs = ['temp_chunks', 'output_clips', 'models']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ exists")
        else:
            print(f"⚠️  {dir_name}/ does not exist (will be created)")
    
    return True


def test_imports():
    """Test importing main modules"""
    print_header("Testing Module Imports")
    
    modules = [
        'kick_clip_generator',
        'gradio_interface',
        'kick_api',
        'config'
    ]
    
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module} - ERROR: {e}")
            all_ok = False
    
    return all_ok


def test_basic_functionality():
    """Test basic functionality"""
    print_header("Testing Basic Functionality")
    
    try:
        from kick_clip_generator import KickClipGenerator, AudioAnalyzer, VideoAnalyzer
        from kick_api import KickAPI
        
        # Test initialization
        print("Testing KickClipGenerator initialization...")
        generator = KickClipGenerator()
        print("✅ KickClipGenerator initialized")
        
        print("Testing AudioAnalyzer initialization...")
        audio_analyzer = AudioAnalyzer()
        print("✅ AudioAnalyzer initialized")
        
        print("Testing VideoAnalyzer initialization...")
        video_analyzer = VideoAnalyzer()
        print("✅ VideoAnalyzer initialized")
        
        print("Testing KickAPI initialization...")
        kick_api = KickAPI()
        print("✅ KickAPI initialized")
        
        # Test URL parsing
        test_url = "https://kick.com/testchannel"
        channel = kick_api.extract_channel_from_url(test_url)
        if channel == "testchannel":
            print("✅ URL parsing works")
        else:
            print(f"⚠️  URL parsing returned: {channel}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  KICK CLIP GENERATOR - SYSTEM TEST")
    print("="*60)
    
    results = {
        'Python Version': check_python_version(),
        'FFmpeg': check_ffmpeg(),
        'Dependencies': check_dependencies(),
        'Directories': check_directories(),
        'Module Imports': test_imports(),
        'Basic Functionality': test_basic_functionality()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYou can now run the application:")
        print("  GUI mode: python main.py --gui")
        print("  CLI mode: python main.py --url <stream_url> --generate-clips")
        print("\nOr use the quick start script:")
        print("  Windows: run.bat")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running the application.")
        print("\nCommon fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Install FFmpeg: https://ffmpeg.org/download.html")
        print("  - Update Python to 3.8 or higher")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
