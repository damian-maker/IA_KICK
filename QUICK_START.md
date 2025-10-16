# 🚀 Quick Start Guide

## Installation (5 minutes)

### 1. Install FFmpeg
**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable

**Quick test:** Open command prompt and type `ffmpeg -version`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test Installation
```bash
python test_system.py
```

## Usage

### 🖥️ GUI Mode (Recommended)

**Windows:**
```bash
run.bat
```

**Or manually:**
```bash
python main.py --gui
```

Then open your browser to: http://localhost:7860

### 📋 CLI Mode

**Analyze a stream:**
```bash
python main.py --url "https://kick.com/channelname"
```

**Generate clips:**
```bash
python main.py --url "https://kick.com/channelname" --generate-clips
```

**Custom settings:**
```bash
python main.py --url "stream.m3u8" --clip-duration 45 --min-gap 15 --generate-clips --type both
```

## Common Issues

### ❌ "FFmpeg not found"
- Install FFmpeg and add to PATH
- Restart terminal/command prompt after installation

### ❌ "Module not found"
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory

### ❌ "403 Error"
- The system automatically retries with different headers
- If persistent, the stream may require authentication

### ❌ "Out of memory"
- Reduce chunk duration in config.py
- Close other applications
- Process shorter streams first

## Tips

1. **First Run**: Start with a short stream (1-2 hours) to test
2. **Performance**: Adjust `FRAME_SKIP` in config.py for faster processing
3. **Quality**: The ML model improves after processing 3-5 streams
4. **Output**: Check `output_clips/` folder for generated clips

## Next Steps

1. ✅ Process your first stream
2. ✅ Review the generated highlights
3. ✅ Adjust settings in `config.py` if needed
4. ✅ Process more streams to improve ML model

## Support

- Check README.md for detailed documentation
- Review logs for error messages
- Test with `test_system.py` to verify installation

---

**Ready to go!** 🎉 Run `python main.py --gui` to start!
