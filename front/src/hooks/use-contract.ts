import abi from "@/lib/contract";
import { message } from "antd";
import { useWriteContract, useAccount, useReadContract } from "wagmi";

export const useContract = () => {
  const { writeContractAsync } = useWriteContract();

  const { isConnected } = useAccount();

  const address = (process.env.NEXT_PUBLIC_CONTRACT_ADDRESS || "") as `0x`;

  async function registerModel(model: {
    name: string;
    description?: string;
    price?: number;
    readmeLink?: string;
    modelFolderLink?: string;
  }) {
    const {
      name: _name,
      description: _description,
      price: _price,
      readmeLink: _readmeLink,
      modelFolderLink: _modelFolderLink,
    } = model;

    if (!isConnected || !address) {
      message.error("请先连接钱包");
      return "";
    }
    const price = _price ? _price * 10 ** 18 : 0;
    try {
      const modelId = await writeContractAsync({
        address,
        abi,
        functionName: "registerModel",
        args: [_name, _description, price, _modelFolderLink, _readmeLink],
      });
      return modelId;
    } catch (error) {
      console.error("Error registering model:", error);
      message.error("注册模型失败，请稍后重试");
      return "";
    }
  }

  const getModelListByPage = (pageNumber: number, pageSize: number) => {
    const result = useReadContract({
      address,
      abi,
      functionName: "getModelSummariesPaginated",
      args: [pageNumber, pageSize],
    });

    console.log("models", Array.isArray(result) ? result[0] : []);
    const { data, isLoading, error } = result;

    return { data, isLoading, error };
  };

  return { registerModel, getModelListByPage };
};
