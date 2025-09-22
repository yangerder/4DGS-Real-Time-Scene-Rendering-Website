import React, { useState } from 'react'
import axios from 'axios'

function App() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState("")
  const [progress, setProgress] = useState(0)
  const [taskId, setTaskId] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState(null)
  const [mode, setMode] = useState("single") // or "multiple"
  const [files, setFiles] = useState([])
  const [datasetName, setDatasetName] = useState("")
  const [multiVideoUrl, setMultiVideoUrl] = useState(null)        // 預覽影片 (cam01)
  const [multiDownloadUrl, setMultiDownloadUrl] = useState(null)  // 點雲 .ply 檔下載




  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage("📥 Ready to upload.")
    setProgress(0)
  }

  const handleUpload = async () => {
    setMessage("")
    setProgress(0)

    if (mode === "single") {
      if (!file) return setMessage("❗ Please select a video first.")

      const formData = new FormData()
      formData.append("file", file)

      try {
        setMessage("🚀 Uploading video...")
        const res = await axios.post("http://localhost:8000/upload_and_extract", formData, {
          onUploadProgress: (progressEvent) => {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setProgress(Math.min(percent * 0.5, 50))
          },
        })

        setMessage("📸 Running COLMAP...")
        setProgress(80)
        await new Promise((r) => setTimeout(r, 2000))

        setMessage(`✅ Finished!\n🆔 Task ID: ${res.data.task_id}`)
        setProgress(100)

        setVideoUrl(`http://localhost:8000/get_video/${res.data.task_id}`)
        setDownloadUrl(`http://localhost:8000/download_pointcloud/${res.data.task_id}`)
      } catch (err) {
        setMessage("❌ Upload or processing failed.")
      }

    } else if (mode === "multiple") {
      if (!datasetName || files.length === 0) {
        setMessage("❗ Dataset name and multiple videos are required.")
        return
      }

      const formData = new FormData()
      formData.append("dataset_name", datasetName)
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i])
      }

      try {
        setVideoUrl(null)  // 🔍 清除舊資料
        setDownloadUrl(null)

        setMessage("🚀 Uploading multiple videos...")
        await axios.post("http://localhost:8000/upload_multiview", formData)
        setProgress(50)

        setMessage("🧠 Processing multiple-view dataset...")
        await axios.post("http://localhost:8000/process_multiview", new URLSearchParams({ dataset_name: datasetName }))
        setProgress(100)

        setMessage(`✅ Multi-view processing done for dataset "${datasetName}"`)
        setMultiVideoUrl(`http://localhost:8000/multiview_video/${datasetName}/cam01.mp4`)
        setMultiDownloadUrl(`http://localhost:8000/multiview_pointcloud/${datasetName}/points3D_multipleview.zip`)

      } catch (err) {
        console.error(err)
        setMessage("❌ Upload or processing failed.")
        setProgress(0)
      }
    }
  }



  return (

    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">

      {/* ⏩ 手動啟動viewer */}
      {/*
      <div className="absolute top-4 right-4">
        <button
          onClick={async () => {
            try {
              const id = prompt("Enter Task ID to launch viewer:");
              if (!id) return;
              await axios.post(`http://localhost:8000/launch_viewer/${id}?env=willi_gspl&port=8081`);
              window.open(`http://localhost:8081/`, "_blank");
            } catch (err) {
              alert("❌ Failed to launch viewer.");
              console.error(err);
            }
          }}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded"
        >
          🔧 Launch Viewer (Manual)
        </button>
      </div>
      /*}

      {/* ⏩ 手動載入已完成的 taskId */}
      <div className="absolute top-4 right-4">
        <button
          onClick={async () => {
            const id = prompt("Enter Task ID to load existing results:");
            if (!id) return;
            try {
              setTaskId(id);
              setVideoUrl(`http://localhost:8000/get_video/${id}`);
              setDownloadUrl(`http://localhost:8000/download_pointcloud/${id}`);
              setMessage(`✅ Loaded results for task: ${id}`);
              setProgress(100);
            } catch (err) {
              console.error(err);
              setMessage("❌ Failed to load existing results.");
              setProgress(0);
            }
          }}
          className="mt-4 bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded w-full"
        >
          ⏩ Load Existing Task ID
        </button>
      </div>


      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">🎬 Upload Video for 4DGS</h1>

        {/* 模式選擇 */}
        <div className="mb-4">
          <label className="mr-4 font-semibold">Mode:</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="border px-2 py-1 rounded"
          >
            <option value="single">Single View</option>
            <option value="multiple">Multi View</option>
          </select>
        </div>

        {/* 上傳欄位 */}
        {mode === "single" ? (
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setFile(e.target.files[0])}
            className="mb-4"
          />
        ) : (
          <div className="space-y-2 mb-4">
            <input
              type="text"
              placeholder="Enter dataset name"
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              className="w-full border px-2 py-1 rounded"
            />
            <input
              type="file"
              accept="video/*"
              multiple
              onChange={(e) => setFiles(e.target.files)}
            />
          </div>
        )}

        {/* 上傳按鈕 */}
        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition w-full"
        >
          Upload
        </button>

        {/* 進度條 */}
        {progress > 0 && (
          <div className="mt-4 w-full bg-gray-300 rounded">
            <div
              className="bg-green-500 text-xs font-bold text-white text-center py-1 rounded transition-all duration-500"
              style={{ width: `${progress}%` }}
            >
              {Math.round(progress)}%
            </div>
          </div>
        )}

        {/* 狀態訊息 */}
        <div className="mt-4 text-sm text-gray-700 whitespace-pre-line">
          {message}
        </div>

        {/* ✅ Single View 顯示結果 */}
        {/*
        {videoUrl && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-2">🎥 Result Preview</h2>
            <video controls className="w-full rounded-lg">
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            {downloadUrl && (
              <a
                href={downloadUrl}
                className="mt-4 inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                download
              >
                ⬇️ Download Point Cloud
              </a>
            )}
          </div>
        )}
        */}

        {videoUrl && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-2">🎥 Result Preview</h2>
            <video controls className="w-full rounded-lg">
              <source src={videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>

            {downloadUrl && (
              <a
                href={downloadUrl}
                className="mt-4 inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                download
              >
                ⬇️ Download Point Cloud
              </a>
            )}

            {taskId && (
              <div className="mt-2 space-y-2">
                {/* 1️⃣ 啟動 Viewer */}
                <button
                  onClick={async () => {
                    try {
                      await axios.post(`http://localhost:8000/launch_viewer/${taskId}?env=willi_gspl`)
                      window.open(`http://localhost:8081/`, "_blank")
                    } catch (err) {
                      alert("❌ Failed to launch viewer.")
                      console.error(err)
                    }
                  }}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded w-full"
                >
                  🔧 Launch Viewer
                </button>
              </div>
            )}
          </div>
        )}


        {/* ✅ Multi View 顯示結果 */}
        {mode === "multiple" && multiVideoUrl && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-2">🎥 Multi-View Preview</h2>
            <video controls className="w-full rounded-lg">
              <source src={multiVideoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
            {multiDownloadUrl && (
              <a
                href={multiDownloadUrl}
                className="mt-4 inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                download
              >
                ⬇️ Download Multi-View Point Cloud
              </a>
            )}
          </div>
        )}

      </div>
    </div>
  )

}

export default App
