import cv2
import os
import sys
import json
import random
import logging
from tqdm import tqdm
import colorlog

# 配置带颜色的日志
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s [V2I for WW] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

# log配置
logger = colorlog.getLogger('V2I for WW')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 加载文本内容
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
file_str = os.path.join(bundle_dir, 'texts.json')
with open(file_str, 'r', encoding='utf-8') as f:
    texts = json.load(f)

# 获取文本中的随机内容
def get_random_message(key):
    return random.choice(texts[key])

# 创建输出路径
def create_sequential_output_dir(base_dir, video_name):  
    index = 1  
    while True:  
        output_dir = f"{base_dir}_{video_name}_{index}"  
        if not os.path.exists(output_dir):  
            os.makedirs(output_dir)  
            return output_dir  
        index += 1  

# 调整视频速率
def adjust_video_duration_and_extract_frames(video_path, output_fps, output_duration, output_dir, output_resolution=None):  
    # 打印视频文件名  
    video_name = os.path.splitext(os.path.basename(video_path))[0]  
    logger.info(f"🔍 正在打开视频文件: {video_name}...")  
        
    # 加载视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(get_random_message("error_open_video"))
        return None

    logger.info("🎥 视频加载成功，开始处理...")

    # 视频处理
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    original_duration = total_frames / original_fps

    time_scale = original_duration / output_duration
    scaled_fps = original_fps * time_scale
    step = scaled_fps / output_fps

    frames = []

    logger.info("⏳ 处理中，请稍候...")
    # 获取并处理帧
    for i in tqdm(range(output_duration * output_fps), desc="处理进度"):
        frame_index = int(i * step - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            logger.warning(get_random_message("video_end_reached"))
            break

        if output_resolution:
            frame = crop_and_resize(frame, output_resolution)

        frames.append(frame)
    
    cap.release()

    # 保存帧到输出目录，并显示进度条
    logger.info("💾 正在保存帧到输出目录...")  
  
    for i, frame in enumerate(tqdm(frames, desc=f"保存进度")):  
        output_frame_path = os.path.join(output_dir, f"home_{i + 1}.jpg")  
        cv2.imwrite(output_frame_path, frame)  
  
    # 处理完成的文本也附上文件名  
    logger.info(get_random_message("frames_saved").format(frame_count=len(frames), output_dir=output_dir, video_name=video_name))  

# 帧尺寸裁剪
def crop_and_resize(frame, output_resolution):
    input_h, input_w = frame.shape[:2]
    target_w, target_h = output_resolution
    aspect_ratio = target_w / target_h

    if input_w / input_h > aspect_ratio:
        new_w = int(input_h * aspect_ratio)
        offset = (input_w - new_w) // 2
        frame = frame[:, offset:offset + new_w]
    else:
        new_h = int(input_w / aspect_ratio)
        offset = (input_h - new_h) // 2
        frame = frame[offset:offset + new_h, :]

    return cv2.resize(frame, output_resolution)

# 信息打印
def print_boxed_info(program_name: str, description: str, author: str, project_link: str, author_link: str):  
    # ANSI颜色代码  
    RED = '\033[91m'  
    GREEN = '\033[92m'  
    YELLOW = '\033[93m'  
    BLUE = '\033[94m'  
    MAGENTA = '\033[95m'  
    CYAN = '\033[96m'  
    WHITE = '\033[97m'  
    RESET = '\033[0m'  
  
    # 边框宽度（根据内容自动调整） 
    max_len = max(len(program_name), len(description), len(author), len(project_link), len(author_link)) + 4  
    program_name = program_name.ljust(max_len * 2 - 2, ' ')
    description = description.ljust(max_len * 2 - 17, ' ')
    author = f"作者: {author}".ljust(max_len * 2 - 4, ' ')
    project_link = f"项目链接: {project_link}".ljust(max_len * 2 - 6, ' ')
    author_link = f"作者主页: {author_link}".ljust(max_len * 2 - 6, ' ')
  
    # 打印顶部边框  
    print('+' + '-' * (max_len * 2) + '+')  
    # 打印内容  
    print(f'| {CYAN}{program_name}{RESET} |')  
    print(f'| {WHITE}{description}{RESET} |')  
    print(f'| {GREEN}{author}{RESET} |')  
    print(f'| {BLUE}{project_link}{RESET} |')  
    print(f'| {MAGENTA}{author_link}{RESET} |')  
    # 打印底部边框  
    print('+' + '-' * (max_len * 2) + '+')  
    
    return max_len

if __name__ == "__main__":  
    # 设置
    output_fps = 30    
    output_duration = 15    
    output_resolution = (1280, 760)    
    
    max_len = print_boxed_info(  
        program_name="V2I for WW v0.1.1",  
        description="一个从视频生成图片序列的小工具",  
        author="QuickLAW",  
        project_link="https://github.com/QuickLAW/V2I-for-WW/",  
        author_link="https://github.com/QuickLAW"  
    )  
    
    logger.debug("当前工作目录: " + os.getcwd())
    # 获取变量
    if len(sys.argv) < 2:    
        logger.error(get_random_message("no_video_path"))    
        sys.exit(1)    
    
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))    
    base_output_dir = os.path.join(exe_dir, "output_frames")    
    video_paths = sys.argv[1:]  # 获取所有视频路径  
    total_videos = len(video_paths)  # 计算视频总数  
    
    # 开始批处理
    current_video_index = 1  # 当前视频序号  
    for video_path in video_paths:    
        video_name = os.path.splitext(os.path.basename(video_path))[0]    
        output_dir = create_sequential_output_dir(base_output_dir, video_name)    
          
        # 在日志中显示当前处理的视频序号  
        logger.info(f"🎬 正在处理视频 【{current_video_index}/{total_videos}】: {video_name}")  
          
        adjust_video_duration_and_extract_frames(video_path, output_fps, output_duration, output_dir, output_resolution)    
          
        # 处理完成的文本也附上文件名  
        logger.info(f"🎉 视频 {video_name} 处理完成！")    
          
        current_video_index += 1  # 更新当前视频序号  
        
        print('=' * (max_len * 2 + 2))  
    logger.info("所有视频处理完成！")    
    print()
    input(get_random_message("processing_finished"))