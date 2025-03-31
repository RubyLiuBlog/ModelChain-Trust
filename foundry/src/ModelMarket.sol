// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ModelMarket {
	// 添加佣金相关变量
	uint public commissionRate; // 佣金比例 (例如: 500 表示 5%)
	address public commissionReceiver; // 佣金接收地址
	address public admin; // 合约管理员
	uint private constant DENOMINATOR = 10000; // 分母，用于计算佣金百分比

	// 修改构造函数，设置初始值
	constructor() {
		admin = msg.sender;
		commissionReceiver = msg.sender; // 初始设置管理员为佣金接收者
		commissionRate = 500; // 默认佣金比例 5%
	}

	struct Report {
		string reportId;
		address executor;
		uint totalScore;
		uint languageScore;
		uint instructScore;
		uint codeScore;
		uint mathScore;
		uint reasoningScore;
		uint knowledgeScore;
	}

	struct Model {
		uint id;
		address owner;
		string name;
		string description;
		string dataLink;
		string readmeLink;
		uint price;
		bool isPublished;
		Report[] reportList;
	}

	// 存储模型摘要信息
	struct ModelSummary {
		uint id;
		address owner;
		string name;
		string description;
		uint price;
	}

	uint private modelIdCounter = 0;
	mapping(uint => Model) public models;
	mapping(address => uint[]) public userModels;
	mapping(uint => mapping(address => bool)) public purchases;

	// 新增映射以检查名称和IPFS哈希是否重复
	mapping(string => bool) private usedModelNames;
	mapping(string => bool) private usedDataLinks;

	event ModelListed(
		uint indexed modelId,
		address indexed owner,
		string name,
		uint price
	);
	event ModelPurchased(uint indexed modelId, address indexed buyer, uint price);
	event ModelUnpublished(uint indexed modelId, address indexed owner);

	// 设置佣金比例的函数
	function setCommissionRate(uint _rate) external {
		require(msg.sender == admin, "Only admin can set commission rate");
		require(_rate <= 3000, "Commission rate cannot exceed 30%"); // 设置上限为30%
		commissionRate = _rate;
	}

	// 设置佣金接收地址的函数
	function setCommissionReceiver(address _receiver) external {
		require(msg.sender == admin, "Only admin can set commission receiver");
		require(_receiver != address(0), "Invalid address");
		commissionReceiver = _receiver;
	}

	// 转移管理员权限的函数
	function transferAdmin(address _newAdmin) external {
		require(msg.sender == admin, "Only admin can transfer admin role");
		require(_newAdmin != address(0), "Invalid address");
		admin = _newAdmin;
	}

	function registerModel(
		string memory _name,
		string memory _description,
		uint _price,
		string memory _dataLink,
		string memory _readmeLink
	) public returns (uint modelId) {
		require(bytes(_name).length > 0, "Name cannot be empty");
		require(!isModelNameUsed(_name), "Model name already exists");
		require(_price >= 0, "Price cannot be null");

		modelId = modelIdCounter++;
		usedModelNames[_name] = true;

		Model storage newModel = models[modelId];
		newModel.id = modelId;
		newModel.owner = msg.sender;
		newModel.name = _name;
		newModel.description = _description;
		newModel.price = _price;
		newModel.dataLink = _dataLink;
		newModel.readmeLink = _readmeLink;
		newModel.isPublished = true;

		userModels[msg.sender].push(modelId);
		emit ModelListed(modelId, msg.sender, _name, _price);
		return modelId;
	}

	// 当模型下架时，释放名称和IPFS哈希以便重用
	function unpublishModel(uint _modelId) public {
		require(models[_modelId].owner == msg.sender, "Not owner");
		models[_modelId].isPublished = false;

		// 释放名称和IPFS哈希
		usedModelNames[models[_modelId].name] = false;
		usedDataLinks[models[_modelId].dataLink] = false;

		emit ModelUnpublished(_modelId, msg.sender);
	}

	function isModelNameUsed(string memory _name) public view returns (bool) {
		return usedModelNames[_name];
	}

	function isDataLinkUsed(string memory _dataLink) public view returns (bool) {
		return usedDataLinks[_dataLink];
	}

	// 修改购买模型的函数以支持佣金
	function purchaseModel(uint _modelId) public payable {
		Model storage model = models[_modelId];
		require(model.isPublished, "Model not available");
		require(!purchases[_modelId][msg.sender], "Already purchased");
		require(model.owner != msg.sender, "Cannot purchase own model");

		if (model.price == 0) {
			require(msg.value == 0, "No payment required");
			purchases[_modelId][msg.sender] = true;
			emit ModelPurchased(_modelId, msg.sender, 0);
		} else {
			require(msg.value >= model.price, "Insufficient funds");
			uint price = model.price;

			// 处理找零
			if (msg.value > price) {
				(bool refundSuccess, ) = payable(msg.sender).call{
					value: msg.value - price
				}("");
				require(refundSuccess, "Refund failed");
			}

			// 更新状态防止重入
			purchases[_modelId][msg.sender] = true;

			// 计算佣金金额
			uint commissionAmount = (price * commissionRate) / DENOMINATOR;
			uint sellerAmount = price - commissionAmount;

			// 转账佣金给接收者
			if (commissionAmount > 0) {
				(bool commissionSuccess, ) = commissionReceiver.call{
					value: commissionAmount
				}("");
				require(commissionSuccess, "Commission transfer failed");
			}

			// 转账剩余金额给卖家
			(bool sellerSuccess, ) = model.owner.call{ value: sellerAmount }("");
			require(sellerSuccess, "Transfer to seller failed");

			emit ModelPurchased(_modelId, msg.sender, price);
		}
	}

	function hasAccess(uint _modelId, address _user) public view returns (bool) {
		return models[_modelId].owner == _user || purchases[_modelId][_user];
	}

	function getUserModels(address _user) public view returns (uint[] memory) {
		return userModels[_user];
	}

	function getModelDetails(uint _modelId) public view returns (Model memory) {
		Model memory modelCopy = models[_modelId];
		// 检查调用者是否是拥有者或购买者
		if (!(modelCopy.owner == msg.sender || purchases[_modelId][msg.sender])) {
			// 若不是，清空 dataLink
			modelCopy.dataLink = "";
		}
		return modelCopy;
	}

	function getAllModels() public view returns (uint[] memory) {
		uint[] memory liveModels = new uint[](modelIdCounter);
		uint count = 0;
		for (uint i = 0; i < modelIdCounter; i++) {
			if (models[i].isPublished) {
				liveModels[count++] = i;
			}
		}

		// 压缩数组大小
		uint[] memory result = new uint[](count);
		for (uint i = 0; i < count; i++) {
			result[i] = liveModels[i];
		}
		return result;
	}

	// 分页获取模型摘要
	function getModelSummariesPaginated(
		uint _offset,
		uint _limit
	) public view returns (ModelSummary[] memory, uint) {
		// 首先计算总共有多少个已上架的模型
		uint[] memory publishedModelIds = new uint[](modelIdCounter);
		uint publishedCount = 0;

		for (uint i = 0; i < modelIdCounter; i++) {
			if (models[i].isPublished) {
				publishedModelIds[publishedCount++] = i;
			}
		}

		// 计算当前页面要返回多少个模型
		uint remainingItems = publishedCount > _offset
			? publishedCount - _offset
			: 0;
		uint itemsToReturn = remainingItems < _limit ? remainingItems : _limit;

		// 创建返回结果数组
		ModelSummary[] memory result = new ModelSummary[](itemsToReturn);

		// 填充结果数组
		for (uint i = 0; i < itemsToReturn; i++) {
			uint modelId = publishedModelIds[_offset + i];
			Model storage model = models[modelId];

			result[i] = ModelSummary({
				id: model.id,
				owner: model.owner,
				name: model.name,
				description: model.description,
				price: model.price
			});
		}

		// 返回结果和总数
		return (result, publishedCount);
	}

	function addModelReport(
		uint _modelId,
		string memory _reportId,
		uint _totalScore,
		uint _languageScore,
		uint _instructScore,
		uint _codeScore,
		uint _mathScore,
		uint _reasoningScore,
		uint _knowledgeScore
	) public {
		Model storage model = models[_modelId];
		require(model.owner == msg.sender, "Only owner can add report");
		require(model.isPublished, "Model not available");
		// 添加报告
		model.reportList.push(
			Report({
				reportId: _reportId,
				executor: msg.sender,
				totalScore: _totalScore,
				languageScore: _languageScore,
				instructScore: _instructScore,
				codeScore: _codeScore,
				mathScore: _mathScore,
				reasoningScore: _reasoningScore,
				knowledgeScore: _knowledgeScore
			})
		);
	}

	function updataModelDataLinkByAdminUser(
		uint _modelId,
		string memory _dataLink,
		string memory _readmeLink
	) public returns (bool) {
		require(msg.sender == admin, "Only admin can update data link");
		Model storage model = models[_modelId];
		model.dataLink = _dataLink;
		model.readmeLink = _readmeLink;
		return true;
	}

	function getModelReportList(
		uint _modelId
	) public view returns (Report[] memory) {
		return models[_modelId].reportList;
	}
	function getModelReport(
		uint _modelId,
		uint _reportId
	) public view returns (Report memory) {
		return models[_modelId].reportList[_reportId];
	}
}
