# Quick Start: Clip Viewing, Rating & Model Improvement

## 🚀 Getting Started in 3 Steps

### Step 1: Generate Clips
```bash
python main.py --gui
```

1. Open the web interface (default: http://localhost:7860)
2. Go to "🎥 Generate Clips" tab
3. Enter a stream URL
4. Click "Analyze Stream"
5. Click "Generate Clips"

### Step 2: Rate Your Clips
1. Go to "⭐ View & Rate Clips" tab
2. Click "Load Clips for Rating"
3. Watch each clip
4. Select a rating (1-5 stars)
5. Click "Submit Rating"

### Step 3: Train the Model
- **Automatic**: Model trains every 5 ratings
- **Manual**: Click "Train Model Now" button
- **Minimum**: Need 10 rated clips to start

## 📊 What Happens Next?

### After Rating 10+ Clips:
✅ Model learns your preferences  
✅ Future highlights match your taste  
✅ Better clips generated automatically  

### Rating Guide:
- ⭐ **1 star**: Not a highlight, boring
- ⭐⭐ **2 stars**: Weak highlight
- ⭐⭐⭐ **3 stars**: Decent highlight
- ⭐⭐⭐⭐ **4 stars**: Good highlight
- ⭐⭐⭐⭐⭐ **5 stars**: Perfect highlight!

## 💾 Browse & Download

Go to "📂 Browse & Download" tab to:
- View all generated clips in a gallery
- Download individual clips
- See ratings and scores

## 🎓 Model Improvement Cycle

```
Generate Clips → Rate Clips → Model Trains → Better Clips → Repeat
```

The more you rate, the smarter the AI becomes!

## 📈 Track Progress

In the "⭐ View & Rate Clips" tab:
1. Click "Refresh Statistics"
2. View:
   - Total clips generated
   - Number of rated clips
   - Average rating
   - Model training status

## 🔧 Tips

1. **Be consistent** with your ratings
2. **Rate variety** - both good and bad clips
3. **Rate regularly** - model improves with more data
4. **Check statistics** - ensure balanced ratings

## 🎯 Example Workflow

```
Day 1: Generate 20 clips from a stream
Day 1: Rate all 20 clips (takes ~5 minutes)
Day 1: Model trains automatically
Day 2: Generate clips from new stream
Day 2: Notice improved highlight detection!
Day 2: Rate new clips to further improve
```

## ❓ FAQ

**Q: How many clips should I rate?**  
A: Minimum 10 to start, but 50+ gives best results

**Q: Can I change my ratings?**  
A: Yes, just rate the same clip again

**Q: What if I disagree with the AI?**  
A: That's perfect! Your ratings teach it your preferences

**Q: How long does training take?**  
A: Usually 1-5 seconds with 10-50 clips

**Q: Where are clips stored?**  
A: `output_clips/` directory and `clips.db` database

## 🚨 Troubleshooting

**No clips to rate?**  
→ Generate clips first in the Generate tab

**Model won't train?**  
→ Need at least 10 rated clips

**Gallery is empty?**  
→ Click "Refresh Gallery" button

---

**Ready to improve your AI? Start rating clips now!** 🎬⭐
