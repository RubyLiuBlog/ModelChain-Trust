"use client";
// app/register/page.tsx
import React, { Suspense, useState } from "react";
import { motion } from "framer-motion";
import { Button, Form, Input, InputNumber, Upload, Space, message } from "antd";
import { UploadOutlined } from "@ant-design/icons";
import dynamic from "next/dynamic";
import { API, CommonResponse } from "@/lib/httpClient";
import { useContract } from "@/hooks/use-contract";
import { useAccount } from "wagmi";

const EditorComp = dynamic(() => import("../../components/EditorComponent"), {
  ssr: false,
});

const markdown = `
# 模型说明
## 模型名称
## 模型描述
## 模型使用方法
## 模型评测方法
## 模型评测结果
## 模型许可证
## 模型作者
`;

export default function RegisterModelPage() {
  const { registerModel } = useContract();
  const { isConnected } = useAccount();
  const [sourceFileList, setSourceFileList] = useState<any[]>([]);
  const [form] = Form.useForm();

  const onReset = () => {
    form.resetFields();
  };

  const onFinish = async (values: {
    name: string;
    description: string;
    price: number;
    readme: string;
  }) => {
    console.log("Received values of form: ", isConnected);
    if (isConnected) {
      if (sourceFileList.length === 0) {
        message.error("请上传模型源文件");
        return;
      }
      try {
        const modelId = await registerModel({
          name: values.name,
          description: values.description,
          price: values.price,
          readmeLink: "",
          modelFolderLink: "",
        });
        if (!modelId) {
          message.error("注册模型失败，请稍后重试");
          return;
        }
        const formData = new FormData();
        formData.append("filename", sourceFileList[0]);
        formData.append(
          "readme",
          new Blob([values.readme], { type: "text/markdown" })
        );
        formData.append("modelId", modelId);
        const res = await API.post<CommonResponse>("/ai/model", formData);
        if (res.success) {
          message.success("上传成功,请查看任务队列");
        }
      } catch (error) {
        console.error(error);
        message.error("上传失败，请稍后重试");
      }
    } else {
      message.error("请先连接钱包");
    }
  };

  return (
    <div className="container mx-auto py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold mb-8">注册新模型</h1>
        <Form
          name="basic"
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          style={{ maxWidth: 600 }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          form={form}
          autoComplete="off"
        >
          <Form.Item
            label="模型名称"
            name="name"
            rules={[{ required: true, message: "请输入你的模型名称" }]}
          >
            <Input />
          </Form.Item>

          <Form.Item label="模型描述" name="description">
            <Input.TextArea />
          </Form.Item>

          <Form.Item
            label="模型价格"
            name="price"
            rules={[{ required: true, message: "请输入你的模型价格" }]}
          >
            <InputNumber
              style={{ width: 200 }}
              min="0"
              max="10"
              step="0.00000000000001"
              stringMode
              suffix="ETH"
            ></InputNumber>
          </Form.Item>
          <Form.Item label="模型README" name="readme">
            <Suspense fallback={null}>
              <EditorComp initialValue={markdown} />
            </Suspense>
          </Form.Item>
          <Form.Item label="模型源文件" valuePropName="fileList" required>
            <Upload
              accept=".zip,.rar"
              multiple={false}
              maxCount={1}
              beforeUpload={(file) => {
                setSourceFileList([file]);
                return false;
              }}
            >
              <Button icon={<UploadOutlined />}>上传</Button>
            </Upload>
          </Form.Item>

          <Form.Item label={null}>
            <Space>
              <Button type="primary" htmlType="submit">
                Submit
              </Button>
              <Button htmlType="button" onClick={onReset}>
                Reset
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </motion.div>
    </div>
  );
}
