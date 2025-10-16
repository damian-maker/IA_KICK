"""
FFmpeg/FFprobe Diagnostic Tool
Helps troubleshoot video processing issues
"""

import subprocess
import sys
import os
from pathlib import Path


def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def check_command(cmd_name, cmd_args):
    """Check if a command is available and working"""
    try:
        result = subprocess.run(
            [cmd_name] + cmd_args,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Get first line of output (usually version info)
            first_line = result.stdout.split('\n')[0] if result.stdout else result.stderr.split('\n')[0]
            print(f"✅ {cmd_name} is working")
            print(f"   {first_line}")
            return True
        else:
            print(f"⚠️  {cmd_name} returned error code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print(f"❌ {cmd_name} not found in PATH")
        print(f"   Command '{cmd_name}' is not recognized")
        return False
    except subprocess.TimeoutExpired:
        print(f"⚠️  {cmd_name} timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking {cmd_name}: {e}")
        return False


def check_path():
    """Check PATH environment variable"""
    print_section("Checking PATH")
    
    path_var = os.environ.get('PATH', '')
    paths = path_var.split(os.pathsep)
    
    print(f"Found {len(paths)} directories in PATH")
    
    # Look for FFmpeg in PATH
    ffmpeg_paths = []
    for p in paths:
        path_obj = Path(p)
        if path_obj.exists():
            # Check for ffmpeg.exe or ffmpeg
            if (path_obj / 'ffmpeg.exe').exists() or (path_obj / 'ffmpeg').exists():
                ffmpeg_paths.append(str(path_obj))
    
    if ffmpeg_paths:
        print(f"\n✅ Found FFmpeg in PATH:")
        for p in ffmpeg_paths:
            print(f"   {p}")
    else:
        print("\n❌ FFmpeg not found in any PATH directory")
        print("\nCommon FFmpeg locations to check:")
        common_paths = [
            r"C:\ffmpeg\bin",
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
            r"%USERPROFILE%\ffmpeg\bin"
        ]
        for p in common_paths:
            print(f"   {p}")


def test_ffprobe_on_file():
    """Test ffprobe on a test pattern"""
    print_section("Testing FFprobe Functionality")
    
    try:
        # Try to probe a test URL (this is a public test stream)
        test_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        
        print(f"Testing with URL: {test_url}")
        print("This may take a few seconds...")
        
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', test_url],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0 and result.stdout:
            print("✅ FFprobe can successfully probe streams")
            
            # Try to parse JSON
            import json
            try:
                data = json.loads(result.stdout)
                if 'streams' in data:
                    print(f"   Found {len(data['streams'])} stream(s)")
                if 'format' in data:
                    duration = data['format'].get('duration', 'unknown')
                    print(f"   Duration: {duration}")
            except:
                pass
            
            return True
        else:
            print("⚠️  FFprobe could not probe the test stream")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}")
            return False
            
    except FileNotFoundError:
        print("❌ ffprobe command not found")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  FFprobe test timed out (network issue?)")
        return False
    except Exception as e:
        print(f"❌ Error testing ffprobe: {e}")
        return False


def test_python_ffmpeg():
    """Test python ffmpeg-python library"""
    print_section("Testing Python ffmpeg-python Library")
    
    try:
        import ffmpeg
        print("✅ ffmpeg-python library is installed")
        
        # Try to get ffmpeg version through the library
        try:
            test_url = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
            print(f"\nTesting ffmpeg.probe() with: {test_url}")
            print("This may take a few seconds...")
            
            probe = ffmpeg.probe(test_url, timeout=15)
            print("✅ ffmpeg.probe() is working")
            
            if 'streams' in probe:
                print(f"   Found {len(probe['streams'])} stream(s)")
            if 'format' in probe:
                duration = probe['format'].get('duration', 'unknown')
                print(f"   Duration: {duration}")
            
            return True
            
        except ffmpeg.Error as e:
            print("❌ ffmpeg.probe() failed")
            error_msg = e.stderr.decode() if e.stderr else str(e)
            print(f"   Error: {error_msg[:200]}")
            return False
        except Exception as e:
            print(f"❌ Error calling ffmpeg.probe(): {e}")
            return False
            
    except ImportError:
        print("❌ ffmpeg-python library not installed")
        print("   Install with: pip install ffmpeg-python")
        return False


def provide_solutions():
    """Provide solutions based on findings"""
    print_section("Recommended Solutions")
    
    print("""
If FFmpeg/FFprobe is not found:

1. **Download FFmpeg:**
   - Windows: https://www.gyan.dev/ffmpeg/builds/
   - Download the "ffmpeg-release-essentials.zip"
   
2. **Extract FFmpeg:**
   - Extract to C:\\ffmpeg
   - The bin folder should contain: ffmpeg.exe, ffprobe.exe, ffplay.exe
   
3. **Add to PATH:**
   - Search "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add: C:\\ffmpeg\\bin
   - Click OK and restart terminal
   
4. **Verify Installation:**
   - Open new terminal
   - Run: ffmpeg -version
   - Run: ffprobe -version
   
5. **Test Again:**
   - Run: python diagnose_ffmpeg.py
   - Run: python test_system.py

If ffmpeg.probe() fails but ffprobe works:
   - Check internet connection
   - Try with a local video file instead
   - Check if URL requires authentication
   - Verify URL is accessible in browser
""")


def main():
    print("="*60)
    print("  FFmpeg/FFprobe Diagnostic Tool")
    print("="*60)
    
    results = {}
    
    # Check PATH
    check_path()
    
    # Check FFmpeg
    print_section("Checking FFmpeg")
    results['ffmpeg'] = check_command('ffmpeg', ['-version'])
    
    # Check FFprobe
    print_section("Checking FFprobe")
    results['ffprobe'] = check_command('ffprobe', ['-version'])
    
    # Test FFprobe functionality
    if results['ffprobe']:
        results['ffprobe_test'] = test_ffprobe_on_file()
    else:
        results['ffprobe_test'] = False
    
    # Test Python library
    results['python_ffmpeg'] = test_python_ffmpeg()
    
    # Summary
    print_section("Summary")
    
    all_ok = True
    for check, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.replace('_', ' ').title()}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\n✅ All checks passed! Your FFmpeg setup is working correctly.")
    else:
        print("\n❌ Some checks failed. See solutions below.")
        provide_solutions()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
