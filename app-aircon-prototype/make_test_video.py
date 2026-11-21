# -*- coding: utf-8 -*-
"""E2E 검증용 실제 점멸 영상 생성 — LG 실외기 CH21 패턴.
적색 2회 → 녹색 1회, 3.2초 휴지 후 같은 패턴 반복(9.5초, 30fps, 640x480)."""
import numpy as np, cv2, os

W, H, FPS = 640, 480, 30
DUR = 9.5
out_dir = '/workspace/downloads'
os.makedirs(out_dir, exist_ok=True)

# 배경: 어두운 PCB 느낌 (정적 무늬 + 흰 라벨)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
bg = np.zeros((H, W, 3), np.float32)
bg[..., 0] = 26 + 10 * (yy / H)
bg[..., 1] = 30 + 8 * (yy / H)
bg[..., 2] = 34 + 6 * (yy / H)
rng = np.random.default_rng(7)
noise = rng.normal(0, 3.0, (H, W, 1)).repeat(3, axis=2)
bg += noise
# 흰 스티커(정적 밝은 영역) — 자동 ROI 가 여기에 끌리지 않는지 확인용
bg8 = np.clip(bg, 0, 255).astype(np.uint8)
cv2.rectangle(bg8, (40, 40), (200, 96), (210, 210, 205), -1)
cv2.putText(bg8, 'LG PCB', (52, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 60, 60), 2, cv2.LINE_AA)
bg = bg8.astype(np.float32)

LED = (322, 252)
RAD = 15
pulses = [(0.40, 0.75, 'r'), (1.40, 1.75, 'r'), (2.40, 2.75, 'g'),
          (5.60, 5.95, 'r'), (6.60, 6.95, 'r'), (7.60, 7.95, 'g')]


def frame(i, t):
    img = bg.copy()
    flick = 1.0 + 0.012 * np.sin(t * 9.0)          # 노출 흔들림
    img *= flick
    # 꺼진 LED(어두운 렌즈)
    cv2.circle(img, LED, RAD + 2, (45, 45, 48), -1)
    cv2.circle(img, LED, RAD - 4, (28, 28, 30), -1)
    for (t0, t1, c) in pulses:
        if t0 <= t <= t1:
            ramp = min(1.0, (t - t0) / 0.05, (t1 - t) / 0.05)
            if c == 'r':
                col = (40, 40, 250)
                glow = (20, 20, 90)
            else:
                col = (60, 240, 60)
                glow = (20, 90, 20)
            ov = img.copy()
            cv2.circle(ov, LED, RAD + 12, glow, -1)
            img = cv2.addWeighted(ov, 0.55 * ramp, img, 1 - 0.55 * ramp, 0)
            cv2.circle(img, LED, RAD, tuple(int(v * ramp + 30 * (1 - ramp)) for v in col), -1)
            cv2.circle(img, LED, max(2, RAD - 7), tuple(min(255, int(v * 1.15)) for v in col), -1)
    img += rng.normal(0, 1.6, (H, W, 1)).repeat(3, axis=2)
    return np.clip(img, 0, 255).astype(np.uint8)


def write(path, fourcc):
    vw = cv2.VideoWriter(path, fourcc, FPS, (W, H))
    if not vw.isOpened():
        raise SystemExit('writer failed: ' + path)
    n = int(DUR * FPS)
    for i in range(n):
        vw.write(frame(i, i / FPS))
    vw.release()
    print(path, os.path.getsize(path), 'bytes')


tmp_webm = os.path.join(out_dir, '_raw_test_led_ch21.webm')
write(tmp_webm, cv2.VideoWriter_fourcc(*'VP80'))
# 브라우저·아이폰이 바로 재생하는 H.264 mp4 로 변환 (imageio-ffmpeg 동봉 바이너리)
import imageio_ffmpeg, subprocess
ff = imageio_ffmpeg.get_ffmpeg_exe()
final = os.path.join(out_dir, 'test_led_ch21.mp4')
subprocess.run([ff, '-y', '-loglevel', 'error', '-i', tmp_webm, '-c:v', 'libx264',
                '-preset', 'veryfast', '-crf', '26', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', final], check=True)
os.remove(tmp_webm)
print(final, os.path.getsize(final), 'bytes')
