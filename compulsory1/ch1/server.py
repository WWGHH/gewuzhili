from flask import Flask, request, jsonify, send_file
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import time
import os
import threading

app = Flask(__name__)

# 密钥存储，格式：{key_id: {key: bytes, iv: bytes, timestamp: float}}
keys = {}
# 密钥有效期（秒）
KEY_EXPIRY = 60

# 清理过期密钥的函数
def cleanup_expired_keys():
    while True:
        current_time = time.time()
        expired_keys = [key_id for key_id, key_data in keys.items() if current_time - key_data['timestamp'] > KEY_EXPIRY]
        for key_id in expired_keys:
            del keys[key_id]
        time.sleep(30)

# 启动清理线程
cleanup_thread = threading.Thread(target=cleanup_expired_keys, daemon=True)
cleanup_thread.start()

# 读取原始HTML内容
with open('original_index.html', 'r', encoding='utf-8') as f:
    original_html = f.read()

@app.route('/')
def index():
    # 生成随机密钥和IV
    key = get_random_bytes(32)  # AES-256
    iv = get_random_bytes(16)   # CBC模式需要16字节IV
    
    # 加密HTML内容
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(original_html.encode('utf-8'), AES.block_size))
    encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
    iv_b64 = base64.b64encode(iv).decode('utf-8')
    
    # 生成密钥ID
    key_id = base64.urlsafe_b64encode(get_random_bytes(16)).decode('utf-8')
    
    # 存储密钥
    keys[key_id] = {
        'key': key,
        'iv': iv,
        'timestamp': time.time()
    }
    
    # 读取模板文件
    with open('dynamic_encrypted_index.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 替换模板中的占位符
    rendered = template.replace('{{encrypted_content}}', encrypted_b64)
    rendered = rendered.replace('{{iv}}', iv_b64)
    rendered = rendered.replace('{{key_id}}', key_id)
    
    return rendered

@app.route('/get_key/<key_id>')
def get_key(key_id):
    if key_id in keys:
        key_data = keys[key_id]
        # 检查密钥是否过期
        if time.time() - key_data['timestamp'] > KEY_EXPIRY:
            del keys[key_id]
            return jsonify({'error': 'Key expired'}), 404
        
        # 返回Base64编码的密钥
        key_b64 = base64.b64encode(key_data['key']).decode('utf-8')
        return jsonify({'key': key_b64})
    else:
        return jsonify({'error': 'Invalid key ID'}), 404

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(os.path.join('static', filename))

if __name__ == '__main__':
    # 确保static目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # 运行服务器
    app.run(debug=True, host='0.0.0.0', port=5000)
