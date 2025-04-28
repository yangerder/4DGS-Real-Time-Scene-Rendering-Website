import React, { useState } from 'react'
import axios from 'axios'

function App() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState("")
  const [progress, setProgress] = useState(0)
  const [taskId, setTaskId] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage("📥 Ready to upload.")
    setProgress(0)
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage("❗ Please select a file first.")
      return
    }

    const formData = new FormData()
    formData.append("file", file)

    try {
      setMessage("🚀 Uploading video...")

      const res = await axios.post(
        "http://localhost:8000/upload_and_extract",  // ✅ 改這裡（接 colmap 全流程）
        formData,
        {
          onUploadProgress: (progressEvent) => {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setProgress(Math.min(percent * 0.5, 50))  // 上傳最多到 50%
          },
        }
      )

      // 模擬階段式提示
      setMessage("✂️ Extracting frames from video...")
      setProgress(60)
      await new Promise(r => setTimeout(r, 1000))

      setMessage("📸 Running COLMAP (SfM + MVS)...")
      setProgress(80)
      await new Promise(r => setTimeout(r, 2000))

      setMessage(`✅ Finished!\n🆔 Task ID: ${res.data.task_id}\n📂 Output: ${res.data.output_dir}`)
      setProgress(100)

      setTaskId(res.data.task_id);
      setVideoUrl(`http://localhost:8000/get_video/${res.data.task_id}`);
      setDownloadUrl(`http://localhost:8000/download_pointcloud/${res.data.task_id}`);


    } catch (err) {
      console.error(err)
      setMessage("❌ Upload or processing failed.")
      setProgress(0)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <h1 className="text-xl font-bold mb-4">🎬 Upload Video for 4DGS</h1>

        <input type="file" accept="video/*" onChange={handleFileChange} className="mb-4" />

        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition w-full"
        >
          Upload
        </button>

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

        <div className="mt-4 text-sm text-gray-700 whitespace-pre-line">
          {message}
        </div>

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

      </div>
    </div>
  )
}

export default App
