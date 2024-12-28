# %%
import requests
import random
import time
import os

# 用来读写计数的文件名
COUNTER_FILE = "filename_counter.txt"


def load_counter():
    """从文件中读取当前计数值，没有文件或无法读取时，初始返回21。"""
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except ValueError:
            return 67
    else:
        return 67


def save_counter(value):
    """把新的计数写入文件。"""
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        f.write(str(value))


def get_filename():
    """读取计数 -> 生成文件名 -> 计数+1并写回文件 -> 返回文件名"""
    counter = load_counter()
    filename = f"ComfyUI_{counter:05d}_.png"
    # 计数加1存回文件
    save_counter(counter + 1)
    return filename


# 1. 统一管理正向/负向提示词的函数（可以放在单独的模块中）
def get_prompts():
    """
    在这里定义你想要的正向与负向提示词。
    你可以改造成从别的文件或数据库读取，从而实现更灵活的管理。
    """
    positive_text = "A beautiful short-haired girl in a beautiful red dress on the beach"
    negative_text = "text, watermark"

    print("[DEBUG] Current positive prompt:", positive_text)

    return {
        "positive": positive_text,
        "negative": negative_text
    }



# 2. 构建 payload 的函数，把正负向提示词注入进去
def build_payload(random_seed, positive_prompt, negative_prompt):
    """
    根据给定的随机种子、正负向提示词，构造出完整的请求 payload。
    注意：如果 workflow 的 KSampler 节点 ID 或 CLIPTextEncode 节点 ID 变化，需要同步修改。
    """
    payload = {
        "client_id": "6ee61e1836c0439d9a06fd39a62eb83b",
        "prompt": {
            "1": {
                "inputs": {
                    "seed": random_seed,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["6", 0],
                    "positive": ["4", 0],  # 正向提示词的引用
                    "negative": ["5", 0],  # 负向提示词的引用
                    "latent_image": ["7", 0]
                },
                "class_type": "KSampler",
                "_meta": {"title": "K采样器"}
            },
            "2": {
                "inputs": {"samples": ["1", 0], "vae": ["6", 2]},
                "class_type": "VAEDecode",
                "_meta": {"title": "VAE解码"}
            },
            "3": {
                "inputs": {"filename_prefix": "ComfyUI", "images": ["2", 0]},
                "class_type": "SaveImage",
                "_meta": {"title": "保存图像"}
            },
            "4": {
                "inputs": {
                    # 将正向提示词注入这里
                    "text": positive_prompt,
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP文本编码（提示）"}
            },
            "5": {
                "inputs": {
                    # 将负向提示词注入这里
                    "text": negative_prompt,
                    "clip": ["6", 1]
                },
                "class_type": "CLIPTextEncode",
                "_meta": {"title": "CLIP文本编码（提示）"}
            },
            "6": {
                "inputs": {"ckpt_name": "majicmixRealistic_v7.safetensors"},
                "class_type": "CheckpointLoaderSimple",
                "_meta": {"title": "加载检查点"}
            },
            "7": {
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
                "class_type": "EmptyLatentImage",
                "_meta": {"title": "空潜空间图像"}
            }
        },
        "extra_data": {
            "extra_pnginfo": {
                "workflow": {
                    "last_node_id": 7,
                    "last_link_id": 9,
                    "nodes": [
                        {
                            "id": 6,
                            "type": "CheckpointLoaderSimple",
                            "pos": [95.78068542480469, 337.8717041015625],
                            "size": [315, 98],
                            "flags": {},
                            "order": 0,
                            "mode": 0,
                            "inputs": [],
                            "outputs": [
                                {"name": "MODEL", "type": "MODEL", "links": [1], "slot_index": 0},
                                {"name": "CLIP", "type": "CLIP", "links": [8, 9], "slot_index": 1},
                                {"name": "VAE", "type": "VAE", "links": [6], "slot_index": 2}
                            ],
                            "properties": {"Node name for S&R": "CheckpointLoaderSimple"},
                            "widgets_values": ["majicmixRealistic_v7.safetensors"]
                        },
                        {
                            "id": 4,
                            "type": "CLIPTextEncode",
                            "pos": [580.1140747070312, 53.5384635925293],
                            "size": [422.84503173828125, 164.31304931640625],
                            "flags": {},
                            "order": 2,
                            "mode": 0,
                            "inputs": [{"name": "clip", "type": "CLIP", "link": 8}],
                            "outputs": [
                                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [2], "slot_index": 0}
                            ],
                            "properties": {"Node name for S&R": "CLIPTextEncode"},
                            "widgets_values": [
                                # 将正向提示词注入到 workflow 的节点
                                positive_prompt
                            ]
                        },
                        {
                            "id": 5,
                            "type": "CLIPTextEncode",
                            "pos": [559.250244140625, 289.5494689941406],
                            "size": [425.27801513671875, 180.6060791015625],
                            "flags": {},
                            "order": 3,
                            "mode": 0,
                            "inputs": [{"name": "clip", "type": "CLIP", "link": 9}],
                            "outputs": [
                                {"name": "CONDITIONING", "type": "CONDITIONING", "links": [3], "slot_index": 0}
                            ],
                            "properties": {"Node name for S&R": "CLIPTextEncode"},
                            "widgets_values": [
                                # 将负向提示词注入到 workflow 的节点
                                negative_prompt
                            ]
                        },
                        {
                            "id": 2,
                            "type": "VAEDecode",
                            "pos": [1374.114013671875, 55.5384635925293],
                            "size": [210, 46],
                            "flags": {},
                            "order": 5,
                            "mode": 0,
                            "inputs": [
                                {"name": "samples", "type": "LATENT", "link": 5},
                                {"name": "vae", "type": "VAE", "link": 6}
                            ],
                            "outputs": [{"name": "IMAGE", "type": "IMAGE", "links": [7], "slot_index": 0}],
                            "properties": {"Node name for S&R": "VAEDecode"},
                            "widgets_values": []
                        },
                        {
                            "id": 3,
                            "type": "SaveImage",
                            "pos": [1616.114013671875, 56.5384635925293],
                            "size": [210, 270],
                            "flags": {},
                            "order": 6,
                            "mode": 0,
                            "inputs": [{"name": "images", "type": "IMAGE", "link": 7}],
                            "outputs": [],
                            "properties": {},
                            "widgets_values": ["ComfyUI"]
                        },
                        {
                            "id": 7,
                            "type": "EmptyLatentImage",
                            "pos": [612.1769409179688, 534.6304931640625],
                            "size": [315, 106],
                            "flags": {},
                            "order": 1,
                            "mode": 0,
                            "inputs": [],
                            "outputs": [
                                {"name": "LATENT", "type": "LATENT", "links": [4], "slot_index": 0}
                            ],
                            "properties": {"Node name for S&R": "EmptyLatentImage"},
                            "widgets_values": [512, 512, 1]
                        },
                        {
                            "id": 1,
                            "type": "KSampler",
                            "pos": [1000, 300],
                            "size": [315, 262],
                            "flags": {},
                            "order": 4,
                            "mode": 0,
                            "inputs": [
                                {"name": "model", "type": "MODEL", "link": 1},
                                {"name": "positive", "type": "CONDITIONING", "link": 2},
                                {"name": "negative", "type": "CONDITIONING", "link": 3},
                                {"name": "latent_image", "type": "LATENT", "link": 4}
                            ],
                            "outputs": [
                                {"name": "LATENT", "type": "LATENT", "links": [5], "slot_index": 0}
                            ],
                            "properties": {"Node name for S&R": "KSampler"},
                            "widgets_values": [
                                # 0 是占位，下面会用随机数替换
                                0,
                                "randomize",
                                20,
                                8,
                                "euler",
                                "normal",
                                1
                            ]
                        }
                    ],
                    "links": [
                        [1, 6, 0, 1, 0, "MODEL"],
                        [2, 4, 0, 1, 1, "CONDITIONING"],
                        [3, 5, 0, 1, 2, "CONDITIONING"],
                        [4, 7, 0, 1, 3, "LATENT"],
                        [5, 1, 0, 2, 0, "LATENT"],
                        [6, 6, 2, 2, 1, "VAE"],
                        [7, 2, 0, 3, 0, "IMAGE"],
                        [8, 6, 1, 4, 0, "CLIP"],
                        [9, 6, 1, 5, 0, "CLIP"]
                    ],
                    "version": 0.4
                }
            }
        }
    }

    # 将随机种子也同步到 workflow 里的 KSampler 节点
    nodes = payload["extra_data"]["extra_pnginfo"]["workflow"]["nodes"]
    for node in nodes:
        if node["id"] == 1:  # 这里是 KSampler 节点的 id
            node["widgets_values"][0] = random_seed
            break

    return payload


# Step 1: POST 请求以生成 prompt_id
def create_prompt():
    # 先生成一个随机种子
    random_seed = random.randint(1, 999999999999999)

    # 从 get_prompts() 获取正向/负向提示词
    prompts = get_prompts()
    positive_prompt = prompts["positive"]
    negative_prompt = prompts["negative"]

    # 构建请求 payload（把随机种子、正负提示词都传进去）
    payload = build_payload(random_seed, positive_prompt, negative_prompt)

    url = "http://127.0.0.1:8188/api/prompt"
    headers = {
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("POST 请求成功，生成的 prompt_id:", data.get("prompt_id"))
        return data.get("prompt_id")
    else:
        print("POST 请求失败，状态码:", response.status_code)
        print("错误信息:", response.text)
        return None


# Step 2: GET 请求以下载图片
def download_image(filename):
    url = "http://127.0.0.1:8188/api/view"
    params = {
        "filename": filename,
        "subfolder": "",
        "type": "output",
        "rand": str(random.random())  # 避免缓存
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"图片已保存为 '{filename}'")
        else:
            print(f"GET 请求失败，状态码: {response.status_code}")
            print("错误信息:", response.text)
    except requests.RequestException as e:
        print("请求时发生错误:", e)


# 主流程
def main():
    # 这里举例循环1次，你可以改成更多次
    for i in range(1):
        prompt_id = create_prompt()
        if prompt_id:
            # 从文件中取计数，生成文件名，并自增
            filename = get_filename()
            download_image(filename)


if __name__ == "__main__":
    main()
# %%
resps = requests.get("http://127.0.0.1:8188/api/history/72853c46-e5c7-4f9f-87ad-fcb73243d877")
# print(resps.json())
resps.json()
# %%
