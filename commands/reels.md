# Instagram Reel Summarizer

Summarize an Instagram Reel from its URL. Extract the caption, transcribe the audio, and provide a complete summary.

## Input

The user will provide an Instagram Reel URL as the argument: $ARGUMENTS

## Instructions

Follow these steps exactly:

### Step 1: Set up environment

Run this to ensure tools are on PATH:

```
export PATH="$PATH:/c/Users/stans/AppData/Roaming/Python/Python313/Scripts"
```

### Step 2: Create a temp working directory

```
mkdir -p /tmp/reels_tmp && cd /tmp/reels_tmp
```

### Step 3: Download metadata (caption, description)

Run yt-dlp to get the reel's metadata as JSON. Use `--cookies-from-browser chrome` so Instagram doesn't block the request:

```
yt-dlp --cookies-from-browser chrome --write-info-json --skip-download -o "reel" "$URL"
```

Where `$URL` is the Instagram Reel URL provided by the user.

Read the resulting `reel.info.json` file. Extract:
- `description` (this is the caption)
- `title`
- `uploader` / `channel`
- `like_count`, `comment_count` if available
- Any hashtags in the description

### Step 4: Download the audio

```
yt-dlp --cookies-from-browser chrome -x --audio-format wav -o "reel_audio.%(ext)s" "$URL"
```

### Step 5: Transcribe the audio

Use whisper to transcribe the audio file to text:

```
python -m whisper reel_audio.wav --model base --output_format txt --output_dir /tmp/reels_tmp
```

Note: The first run will download the whisper base model (~150MB). This is a one-time download.

Read the resulting `reel_audio.txt` file to get the transcription.

### Step 6: Produce the summary

Using ALL the information gathered (metadata + transcription), produce a structured summary in this format:

---

**Reel by:** [uploader name]

**Caption:** [the original caption/description]

**Hashtags:** [any hashtags found]

**What's spoken in the reel:**
[Full transcription of the audio]

**Summary:**
[A concise 2-4 sentence summary of what the reel is about, combining both the caption context and the spoken content. Mention the topic, key points, and overall purpose/tone.]

**Engagement:** [like count, comment count if available]

---

### Step 7: Clean up

Delete the temporary files:

```
rm -rf /tmp/reels_tmp
```

## Error Handling

- If yt-dlp fails with a login error, tell the user they need to be logged into Instagram in Chrome
- If the reel has no audio or whisper produces empty output, note that and summarize based on the caption/metadata only
- If the URL doesn't look like an Instagram Reel URL, ask the user to provide a valid one
