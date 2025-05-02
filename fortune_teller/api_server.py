"""
Flask API server for the Fortune Teller system.
Uses the main FortuneTeller class to leverage the complete backend logic.
"""
import json
import logging
import datetime
import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入主程序类
from fortune_teller.main import FortuneTeller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fortune_teller_api.log')
    ]
)
logger = logging.getLogger("FortuneAPIServer")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 全局变量
fortune_teller = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    available_systems = fortune_teller.get_available_systems()
    return jsonify({
        "status": "ok",
        "availableSystems": [system["name"] for system in available_systems]
    })

@app.route('/api/systems', methods=['GET'])
def get_systems():
    """Get all available fortune telling systems."""
    systems = fortune_teller.get_available_systems()
    return jsonify({"systems": systems})

@app.route('/api/fortune/bazi', methods=['POST'])
def bazi_fortune():
    """
    Generate a BaZi (Chinese Eight Characters) fortune reading.
    
    Expected JSON input:
    {
        "name": "User's name",
        "birthDate": "YYYY-MM-DD",
        "birthTime": "HH:MM",
        "gender": "male|female",
        "location": "Birth location (optional)",
        "question": "User's question (optional)"
    }
    """
    try:
        data = request.json
        logger.info(f"Received BaZi request: {data}")
        
        # Convert frontend format to FortuneTeller format
        gender_map = {"male": "男", "female": "女"}
        
        input_data = {
            "birth_date": data.get("birthDate"),
            "birth_time": data.get("birthTime"),
            "gender": gender_map.get(data.get("gender")),
            "location": data.get("location"),
            "name": data.get("name", ""),
            "question": data.get("question", "")
        }
        
        # Use the FortuneTeller class to perform the reading
        result = fortune_teller.perform_reading("bazi", input_data)
        
        # Save the reading with a unique ID
        result_id = f"bazi-{hash(data.get('name', '') + data.get('birthDate', ''))}"
        
        # Create a response compatible with the frontend expectations
        frontend_response = convert_to_frontend_format(result, data, result_id)
        
        # Save the result for later retrieval
        save_result(result_id, frontend_response)
        
        # Return the response
        logger.info("Successfully generated BaZi response")
        return jsonify({
            "resultId": result_id,
            "result": frontend_response
        })
        
    except Exception as e:
        logger.error(f"Error processing BaZi request: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400

# In-memory storage for results
results_storage = {}

def save_result(result_id, result):
    """Save a result to storage."""
    results_storage[result_id] = result

@app.route('/api/result/<result_id>', methods=['GET'])
def get_result(result_id):
    """Get a saved result by ID."""
    if result_id in results_storage:
        return jsonify(results_storage[result_id])
    else:
        return jsonify({"error": "结果不存在"}), 404

def convert_to_frontend_format(result, request_data, result_id):
    """
    Convert the FortuneTeller result format to frontend expected format.
    最简单的实现：将LLM的原始响应直接显示出来
    """
    # 提取LLM生成的文本
    full_text = result.get("full_text", "")
    if not full_text:
        full_text = str(result)
    
    # 从结果中提取处理过的数据（八字、五行等）
    processed_data = {}
    if "metadata" in result and isinstance(result["metadata"], dict):
        if "processed_data" in result["metadata"]:
            processed_data = result["metadata"]["processed_data"]
    
    # 创建基本的前端响应
    frontend_response = {
        "id": result_id,
        "name": request_data.get("name", ""),
        "birthDate": request_data.get("birthDate", ""),
        "birthTime": request_data.get("birthTime", ""),
        "gender": request_data.get("gender", ""),
        "location": request_data.get("location", ""),
        "question": request_data.get("question", ""),
        "generatedAt": datetime.datetime.now().isoformat(),
        "analysis": {
            "character": full_text,  # 将完整的LLM响应放入character字段
            "career": "",
            "relationships": "",
            "health": "",
            "fortune": ""
        }
    }
    
    # 添加八字信息（从processed_data中获取，如果不存在则使用默认值）
    try:
        year_stem = "甲"
        year_branch = "子"
        month_stem = "乙"
        month_branch = "丑"
        day_stem = "丙"
        day_branch = "寅"
        hour_stem = "丁"
        hour_branch = "卯"
        
        # 如果有处理过的八字数据，优先使用
        if processed_data and "year_pillar" in processed_data:
            year_stem = processed_data["year_pillar"]["stem"]
            year_branch = processed_data["year_pillar"]["branch"]
            month_stem = processed_data["month_pillar"]["stem"]
            month_branch = processed_data["month_pillar"]["branch"]
            day_stem = processed_data["day_pillar"]["stem"]
            day_branch = processed_data["day_pillar"]["branch"]
            if processed_data.get("hour_pillar"):
                hour_stem = processed_data["hour_pillar"]["stem"]
                hour_branch = processed_data["hour_pillar"]["branch"]
        
        frontend_response["eightWords"] = {
            "year": {
                "heavenlyStem": year_stem,
                "earthlyBranch": year_branch
            },
            "month": {
                "heavenlyStem": month_stem,
                "earthlyBranch": month_branch
            },
            "day": {
                "heavenlyStem": day_stem,
                "earthlyBranch": day_branch
            },
            "hour": {
                "heavenlyStem": hour_stem,
                "earthlyBranch": hour_branch
            }
        }
    except Exception as e:
        logger.error(f"Error setting eight words: {e}")
        # 提供默认的八字信息
        frontend_response["eightWords"] = {
            "year": {"heavenlyStem": "甲", "earthlyBranch": "子"},
            "month": {"heavenlyStem": "乙", "earthlyBranch": "丑"},
            "day": {"heavenlyStem": "丙", "earthlyBranch": "寅"},
            "hour": {"heavenlyStem": "丁", "earthlyBranch": "卯"}
        }
    
    # 添加五行信息
    try:
        wood = "木"
        fire = "火" 
        earth = "土"
        metal = "金"
        water = "水"
        
        # 如果有处理过的五行数据，优先使用
        if processed_data and "elements" in processed_data:
            elements = processed_data["elements"]
            dominant = elements["strongest"]
            lacking = elements["weakest"]
            balanced = [e for e in ["木", "火", "土", "金", "水"] 
                      if e != dominant and e != lacking]
        else:
            # 使用默认值
            dominant = wood
            lacking = metal
            balanced = [fire, earth, water]
        
        frontend_response["fiveElements"] = {
            "dominant": dominant,
            "lacking": lacking,
            "balanced": balanced
        }
    except Exception as e:
        logger.error(f"Error setting five elements: {e}")
        # 默认五行信息
        frontend_response["fiveElements"] = {
            "dominant": "木",
            "lacking": "金",
            "balanced": ["火", "土", "水"]
        }
    
    return frontend_response

def run_server(host='0.0.0.0', port=5000):
    """Run the Flask API server."""
    logger.info(f"Starting Fortune Teller API server on {host}:{port}")
    app.run(host=host, port=port, debug=True)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Fortune Teller API服务器")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--host", default="0.0.0.0", help="监听主机 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="监听端口 (默认: 5000)")
    
    args = parser.parse_args()
    
    # 初始化主程序
    fortune_teller = FortuneTeller(args.config)
    
    # 启动服务器
    run_server(host=args.host, port=args.port)
