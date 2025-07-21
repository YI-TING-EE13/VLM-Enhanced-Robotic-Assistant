# VLM-Enhanced Robotic Assistant

## 🤖 專案簡介

這是一個先進的模組化系統，設計用於透過自然語言指令控制機械手臂。系統整合了視覺語言模型 (VLM) 來實現深度、情境感知的指令理解，利用即時視覺數據來解決歧義問題。系統採用「可插拔」架構，允許輕鬆替換核心組件，如 ASR（自動語音識別）、VLM 和 TTS（文字轉語音）服務。

## ✨ 主要特色

-   **🧠 VLM 驅動的歧義消解**：利用最新的 Gemini 2.5 Flash 模型透過即時影像來解釋模糊指令（例如「拿起那個」）
-   **🔧 模組化可插拔架構**：核心組件圍繞介面建構（`ASRInterface`、`VLMInterface`），讓開發者能輕鬆切換服務（例如 `Whisper` vs. mock ASR、`Gemini API` vs. 本地模型）
-   **🎤 即時麥克風錄音**：支援直接從麥克風錄音，無需預錄音檔
-   **� 持續運行模式**：系統可持續運行，處理多次語音互動，無需重新啟動
-   **🛑 智慧語音關閉**：說「關閉系統」可安全退出，包含語音確認機制
-   **�🗣️ 繁體中文語音互動**：完整的中文語音識別和合成功能
-   **🔐 安全的 API 金鑰管理**：使用 `.env` 檔案安全管理敏感的 API 金鑰
-   **🛡️ 強健的工作流程**：主應用程式迴圈具備全面的錯誤處理和自動恢復
-   **💬 互動式反饋**：使用 TTS 提供語音反饋、詢問澄清問題和確認動作

## 🏗️ 系統架構

系統遵循以 VLM 為中心的順序處理管線：

1.  **輸入**：系統接受兩個主要輸入：
    -   來自用戶的語音指令（從麥克風錄製或 `.wav` 檔案）
    -   工作空間的視覺快照（圖像檔案）

2.  **ASR 模組**：將音頻指令轉錄為文字
    -   **預設**：`WhisperASR`（使用 OpenAI 的 Whisper）
    -   **替代方案**：`FunASR`（用於測試的 mock 實作）

3.  **VLM 核心模組**：將轉錄文字和圖像發送給 VLM
    -   **預設**：`GeminiAPI_VLM`（使用 Google Gemini 2.5 Flash）
    -   **替代方案**：`LocalQwenVL`（自託管模型的 mock）

4.  **任務與反饋模組**：應用程式解析 VLM 的 JSON 回應
    -   如果動作是 `clarify`，`TTS` 模組會說出問題
    -   如果動作是 `shutdown`，系統會要求語音確認後安全關閉
    -   如果動作是指令（例如 `pick_up`），系統透過 TTS 確認動作

5.  **持續運行循環**：系統自動準備下一次互動，直到用戶要求關閉

## 🚀 快速開始

### 📋 先決條件

-   **Python 3.10+**：建議使用 Conda 環境管理
-   **FFmpeg**：Whisper ASR 模型需要 FFmpeg（詳見安裝說明）
-   **Gemini API 金鑰**：需要來自 [Google AI Studio](https://aistudio.google.com/) 的有效 API 金鑰

### 🔧 安裝與設定

1.  **複製專案**：
    ```bash
    git clone <your-repository-url>
    cd VLM-Enhanced-Robotic-Assistant
    ```

2.  **建立 Python 環境**：
    ```bash
    # 使用 Conda（推薦）
    conda create --name vlm_robot_env python=3.10 -y
    conda activate vlm_robot_env
    
    # 或使用 venv
    python -m venv vlm_robot_env
    # Windows
    vlm_robot_env\Scripts\activate
    # macOS/Linux
    source vlm_robot_env/bin/activate
    ```

3.  **安裝依賴套件**：
    ```bash
    pip install -r requirements.txt
    ```

4.  **安裝 FFmpeg**：
    
    **Windows（使用 winget，推薦）**：
    ```powershell
    winget install Gyan.FFmpeg
    ```
    
    **Windows（使用 Chocolatey）**：
    ```powershell
    choco install ffmpeg
    ```
    
    **macOS**：
    ```bash
    brew install ffmpeg
    ```
    
    **Linux**：
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

5.  **設定 API 金鑰**：
    -   將 `.env.example` 重新命名為 `.env`
    -   編輯 `.env` 檔案並添加您的 Gemini API 金鑰：
        ```
        GEMINI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
        ```

### 🎮 執行應用程式

```bash
python main.py
```

## 📖 使用方式

### 🔄 持續運行模式（預設）
1. 執行程式後，系統會初始化所有服務
2. 系統進入持續運行模式，顯示互動計數
3. 每次互動：
   - 看到倒數計時後開始說話（5 秒錄音時間）
   - 系統會分析您的語音和圖像
   - 透過語音獲得回應
   - 自動準備下一次互動

### 🛑 安全關閉系統
1. **語音關閉**：說「關閉系統」
2. **系統確認**：會詢問「您確定要關閉系統嗎？」
3. **語音確認**：
   - 說「是」、「確定」、「好」→ 系統關閉
   - 說「否」、「不」、「取消」→ 繼續運行
4. **快速退出**：按 `Ctrl+C` 立即安全關閉

### 🎤 麥克風模式詳細說明
- **錄音提示**：清楚的倒數計時和視覺提示
- **錄音時長**：預設 5 秒（可在程式中調整）
- **語言支援**：優化的繁體中文語音識別
- **錯誤處理**：錄音失敗自動重試或提示

### 📁 檔案模式
修改 `main.py` 中的設定：
```python
RECORDING_MODE: str = "file"  # 改為 "file"
```

### 🔄 切換服務
在 `AppConfig` 類別中修改服務選擇：
```python
# ASR 服務選擇
ASR_SERVICE: str = "whisper"  # 或 "funasr"（mock）

# VLM 服務選擇  
VLM_SERVICE: str = "gemini"   # 或 "qwen_vl"（mock）
```

## 🧪 測試

執行測試套件來驗證所有模組：

```bash
python run_tests.py
```

## 🔧 擴展系統

### 新增 ASR 模型

1.  **建立類別**：在 `src/asr/` 目錄中建立新檔案
2.  **實作介面**：繼承 `ASRInterface` 並實作 `transcribe` 方法
3.  **更新工廠**：在 `src/asr/__init__.py` 中添加新選項

### 新增 VLM 服務

1.  **建立類別**：在 `src/vlm/` 目錄中建立新檔案
2.  **實作介面**：繼承 `VLMInterface` 並實作 `get_decision` 方法
3.  **更新工廠**：在 `src/vlm/__init__.py` 中添加新選項

## 📁 專案結構

```
VLM-Enhanced-Robotic-Assistant/
├── main.py                    # 主要應用程式進入點（持續運行模式）
├── requirements.txt           # Python 依賴套件
├── .env.example              # API 金鑰範例檔案
├── .env                      # API 金鑰配置檔案
├── README.md                 # 專案說明文件
├── CODE_REVIEW.md            # 程式碼審查報告
├── UPDATE_SUMMARY.md         # 功能更新總結
├── run_tests.py              # 測試執行器
├── src/                      # 源代碼目錄
│   ├── audio_recorder.py     # 音頻錄製模組（麥克風功能）
│   ├── asr/                  # 自動語音識別模組
│   │   ├── __init__.py
│   │   ├── asr_interface.py
│   │   ├── whisper_asr.py
│   │   └── funasr_asr.py
│   ├── vlm/                  # 視覺語言模型模組
│   │   ├── __init__.py
│   │   ├── vlm_interface.py
│   │   ├── gemini_vlm.py     # Gemini 2.5 Flash 整合
│   │   └── local_qwen_vlm.py
│   └── tts/                  # 文字轉語音模組
│       ├── __init__.py
│       └── tts_module.py     # 繁體中文 TTS
└── test_data/                # 測試數據
    ├── test_audio.wav
    └── test_image_*.jpeg
```

## 🐛 故障排除

### 常見問題

1.  **FFmpeg 錯誤**：
    ```
    [WinError 2] 系統找不到指定的檔案
    ```
    **解決方案**：確保 FFmpeg 已安裝並在系統 PATH 中

2.  **API 配額限制**：
    ```
    429 You exceeded your current quota
    ```
    **解決方案**：檢查您的 Gemini API 配額或切換到較輕量的模型

3.  **麥克風權限錯誤**：
    **解決方案**：確保應用程式有麥克風使用權限

4.  **音頻設備問題**：
    **解決方案**：檢查音頻設備是否正常工作，或切換到檔案模式

## 🤝 貢獻

歡迎提交 Pull Request 和 Issue！請確保：
1. 程式碼遵循現有的風格和結構
2. 添加適當的文檔和測試
3. 使用描述性的提交訊息

## 📝 授權

[在此添加您的授權資訊]

## 🙏 致謝

-   OpenAI Whisper 團隊提供優秀的語音識別模型
-   Google 提供 Gemini 視覺語言模型 API
-   Microsoft 提供 Edge TTS 服務

## 🔮 Future Work

### 🚀 短期計劃（1-3 個月）

#### 💬 即時互動功能
- **即時對話模式**：支援連續對話，無需每次重新錄音
- **上下文記憶**：系統記住之前的對話內容和指令歷史
- **語音喚醒詞**：說「小助手」喚醒系統，無需手動啟動
- **多輪對話**：支援複雜的多步驟指令分解和執行

#### 📹 即時串流影像功能
- **即時攝影機輸入**：直接從 USB 攝影機或網路攝影機獲取影像
- **動態場景分析**：實時分析工作場景變化
- **移動物體追蹤**：追蹤和識別移動中的工件
- **多角度視覺**：支援多個攝影機同時輸入

### 🎯 中期計劃（3-6 個月）

#### 🤖 機械手臂整合
- **真實機械手臂控制**：整合 ROS（Robot Operating System）
- **路徑規劃**：智慧避障和最佳路徑計算
- **力回饋控制**：精確的力度控制和安全機制
- **協作模式**：人機協作的安全互動

#### 🧠 AI 能力增強
- **自主學習**：從用戶互動中學習優化回應
- **多模態融合**：結合觸覺、聽覺、視覺的綜合感知
- **意圖預測**：預測用戶下一步可能的指令
- **情境理解**：理解工作環境和任務背景

### 🌟 長期願景（6-12 個月）

#### 🌐 企業級應用
- **多用戶支援**：支援多個操作員同時使用
- **權限管理**：不同用戶的操作權限控制
- **雲端部署**：支援雲端和邊緣計算部署
- **監控儀表板**：即時監控系統狀態和性能指標

#### 🔧 高級功能
- **自動化工作流**：學習並自動化重複性任務
- **品質檢測**：整合機器視覺進行產品品質檢測
- **預測性維護**：預測設備維護需求
- **數據分析**：生產效率和操作模式分析

#### 🌍 擴展性
- **多語言支援**：支援英文、日文、韓文等多種語言
- **行業適配**：適配不同行業的特殊需求
- **標準化介面**：支援工業標準協議和介面
- **第三方整合**：與 ERP、MES 等企業系統整合

### 🔬 研究方向

#### 📚 技術探索
- **大語言模型微調**：針對工業場景的專用模型訓練
- **邊緣 AI 優化**：在資源受限環境下的模型優化
- **聯邦學習**：多工廠間的知識共享而不洩露數據
- **神經符號推理**：結合符號推理和神經網路的混合 AI

#### 🛡️ 安全與可靠性
- **故障容錯**：系統故障時的安全降級機制
- **資料安全**：端到端加密和隱私保護
- **實時響應**：毫秒級的響應時間優化
- **安全認證**：工業安全標準認證（如 ISO 26262）

### 🤝 社群參與

我們歡迎社群貢獻以下方向：
- 📝 **文檔改進**：多語言文檔和教學內容
- 🧪 **測試案例**：更多真實場景的測試案例
- 🔌 **插件開發**：新的 ASR、VLM、TTS 服務整合
- 🎨 **UI/UX 設計**：圖形化使用者介面設計
- 🏭 **行業案例**：不同行業的實際應用案例

---

**加入我們的開發之旅！** 如果您對以上任何功能感興趣，歡迎提交 Issue 討論或直接貢獻程式碼。讓我們一起打造下一代智慧製造的未來！🚀
