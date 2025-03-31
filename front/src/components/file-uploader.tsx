"use client";

// components/FileUploader.tsx
import React, { useRef } from "react";
import useStorage from "@/hooks/use-storage";
import { useStore } from "@/hooks/use-store";

const FileUploader: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const { uploadProgress } = useStore();

  const storage = useStorage({
    uploadUrl: "/api/upload",
    chunkSize: 4 * 1024 * 1024, // 4MB 分块
  });

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      await storage.upload(files);
      // 重置 input 以便同一文件可以再次选择
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleFolderChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      await storage.upload(files);
      // 重置 input 以便同一文件夹可以再次选择
      if (folderInputRef.current) folderInputRef.current.value = "";
    }
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.dataTransfer.items) {
      await storage.upload(event.dataTransfer.items);
    } else if (event.dataTransfer.files) {
      await storage.upload(event.dataTransfer.files);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">文件上传</h2>

      {/* 上传进度条 */}
      {uploadProgress.isUploading && (
        <div className="mb-4">
          <p>
            {uploadProgress.fileName} - {uploadProgress.progress}%
          </p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full"
              style={{ width: `${uploadProgress.progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* 拖放区域 */}
      <div
        className="border-2 border-dashed border-gray-300 p-8 text-center mb-4 rounded-lg"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        拖放文件或文件夹到这里上传
      </div>

      {/* 文件选择按钮 */}
      <div className="flex space-x-4">
        <div>
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            ref={fileInputRef}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer"
          >
            选择文件
          </label>
        </div>

        <div>
          <input
            type="file"
            multiple
            onChange={handleFolderChange}
            ref={folderInputRef}
            className="hidden"
            id="folder-input"
          />
          <label
            htmlFor="folder-input"
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 cursor-pointer"
          >
            选择文件夹
          </label>
        </div>
      </div>

      {/* 上传文件列表 */}
      {Object.keys(storage.fileProgress).length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-2">上传列表</h3>
          <div className="space-y-2">
            {Object.entries(storage.fileProgress).map(
              ([fileName, progress]) => (
                <div
                  key={fileName}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <div>
                    <div className="font-medium">{fileName}</div>
                    <div className="text-sm text-gray-500">
                      {progress.status === "uploading"
                        ? "上传中"
                        : progress.status === "paused"
                        ? "已暂停"
                        : progress.status === "completed"
                        ? "已完成"
                        : progress.status === "error"
                        ? "上传失败"
                        : "等待中"}
                      {" - "}
                      {progress.progress}%
                    </div>
                  </div>
                  <div className="space-x-2">
                    {progress.status === "uploading" && (
                      <button
                        onClick={() => storage.pauseUpload(fileName)}
                        className="px-2 py-1 text-sm bg-yellow-500 text-white rounded"
                      >
                        暂停
                      </button>
                    )}
                    {progress.status === "paused" && (
                      <button
                        onClick={() => storage.resumeUpload(fileName)}
                        className="px-2 py-1 text-sm bg-blue-500 text-white rounded"
                      >
                        继续
                      </button>
                    )}
                    {(progress.status === "uploading" ||
                      progress.status === "paused") && (
                      <button
                        onClick={() => storage.cancelUpload(fileName)}
                        className="px-2 py-1 text-sm bg-red-500 text-white rounded"
                      >
                        取消
                      </button>
                    )}
                  </div>
                </div>
              )
            )}
          </div>

          {/* 批量操作按钮 */}
          {Object.keys(storage.fileProgress).length > 1 && (
            <div className="mt-4 space-x-2">
              <button
                onClick={storage.pauseAllUploads}
                className="px-3 py-1 bg-yellow-500 text-white rounded"
              >
                全部暂停
              </button>
              <button
                onClick={storage.resumeAllUploads}
                className="px-3 py-1 bg-blue-500 text-white rounded"
              >
                全部继续
              </button>
              <button
                onClick={storage.cancelAllUploads}
                className="px-3 py-1 bg-red-500 text-white rounded"
              >
                全部取消
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
