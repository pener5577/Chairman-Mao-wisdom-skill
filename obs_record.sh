#!/bin/bash
# OBS录屏控制脚本 v3 - 修复版
# 正确处理ffmpeg停止，确保文件完整

VIDEOS_DIR="/home/kali/Videos"
mkdir -p "$VIDEOS_DIR"

get_timestamp() {
    date +"%Y%m%d_%H%M%S"
}

PID_FILE="/tmp/recording_ffmpeg.pid"
OUTPUT_FILE=""

start_recording() {
    echo "🎬 开始录屏..."
    
    # Check if already recording
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "⚠️ 已经在录屏中 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    TIMESTAMP=$(get_timestamp)
    OUTPUT_FILE="$VIDEOS_DIR/recording_$TIMESTAMP.mp4"
    
    echo "📁 输出文件: $OUTPUT_FILE"
    echo "📐 分辨率: 1280x800"
    echo "🎯 FPS: 30"
    
    # Start recording in background as kali user
    su - kali -c "DISPLAY=:0 ffmpeg -y \
        -f x11grab \
        -framerate 30 \
        -video_size 1280x800 \
        -i :0 \
        -c:v libx264 \
        -preset ultrafast \
        -crf 23 \
        -pix_fmt yuv420p \
        -movflags +faststart \
        '$OUTPUT_FILE'" &
    
    FFmpeg_PID=$!
    echo $FFmpeg_PID > "$PID_FILE"
    echo "$OUTPUT_FILE" > /tmp/recording_output_file
    
    echo "✅ 录屏已启动 (PID: $FFmpeg_PID)"
    
    # Take preview to verify
    sleep 2
    su - kali -c "DISPLAY=:0 ffmpeg -y -i :0 -frames:v 1 -update 1 /tmp/recording_preview.png" 2>/dev/null
    echo "📸 预览已保存"
}

stop_recording() {
    echo "🛑 停止录屏..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️ 没有正在录屏"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    OUTPUT=$(cat /tmp/recording_output_file 2>/dev/null)
    
    if ! kill -0 $PID 2>/dev/null; then
        echo "⚠️ 进程已结束，但文件可能不完整"
        rm -f "$PID_FILE"
        return 1
    fi
    
    echo "⏹️ 发送停止信号到 PID $PID..."
    # Use SIGINT (Ctrl+C) to gracefully stop - this allows ffmpeg to write moov atom
    kill -INT $PID 2>/dev/null
    
    echo "⏳ 等待ffmpeg完成..."
    # Wait for ffmpeg to finish (max 10 seconds)
    for i in {1..20}; do
        if ! kill -0 $PID 2>/dev/null; then
            echo "✅ ffmpeg已正常停止"
            break
        fi
        sleep 0.5
        echo "  等待中... ($i/20)"
    done
    
    # Force kill if still running
    if kill -0 $PID 2>/dev/null; then
        echo "⚠️ 强制停止..."
        kill -9 $PID 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    
    if [ -n "$OUTPUT" ] && [ -f "$OUTPUT" ]; then
        SIZE=$(stat -c%s "$OUTPUT" 2>/dev/null)
        SIZE_MB=$(echo "scale=2; $SIZE / 1024 / 1024" | bc)
        echo "✅ 录屏已保存: $OUTPUT"
        echo "📦 大小: ${SIZE_MB}MB"
        
        # Copy to accessible location
        cp "$OUTPUT" /tmp/last_recording.mp4
        echo "📋 备份: /tmp/last_recording.mp4"
        
        # Verify file is playable
        if ffprobe -v error "$OUTPUT" 2>&1 | grep -q "moov"; then
            echo "❌ 文件可能损坏 (moov atom missing)"
        else
            echo "✅ 文件验证通过"
        fi
    else
        echo "❌ 录屏文件不存在"
    fi
    
    rm -f /tmp/recording_output_file
}

case "$1" in
    "start")
        start_recording
        ;;
    "stop")
        stop_recording
        ;;
    "status")
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "📹 录屏中... (PID: $(cat $PID_FILE))"
            if [ -f /tmp/recording_output_file ]; then
                echo "📁 文件: $(cat /tmp/recording_output_file)"
            fi
        else
            echo "📹 未录屏"
        fi
        echo ""
        echo "📂 已录制的文件:"
        ls -lh "$VIDEOS_DIR"/recording_*.mp4 2>/dev/null | tail -5 || echo "无"
        ;;
    "preview")
        su - kali -c "DISPLAY=:0 ffmpeg -y -i :0 -frames:v 1 -update 1 /tmp/preview.png" 2>/dev/null
        echo "📸 预览已保存: /tmp/preview.png"
        ;;
    *)
        echo "用法: $0 {start|stop|status|preview}"
        echo ""
        echo "命令:"
        echo "  start   - 开始录屏"
        echo "  stop    - 停止录屏 (正确保存文件)"
        echo "  status  - 查看状态"
        echo "  preview - 预览当前屏幕"
        ;;
esac
