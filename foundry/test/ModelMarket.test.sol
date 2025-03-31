// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "../src/ModelMarket.sol"; // 假设合约文件在 src 目录下

contract ModelMarketTest is Test {
	ModelMarket public market;
	address public admin;
	address public user1;
	address public user2;
	address public commissionReceiver;

	// 添加接收ETH的函数
	receive() external payable {}

	// 设置测试环境
	function setUp() public {
		admin = address(this); // 测试合约作为管理员
		user1 = address(0x1);
		user2 = address(0x2);
		commissionReceiver = address(0x3);

		// 给测试账户充值资金
		vm.deal(user1, 10 ether);
		vm.deal(user2, 10 ether);

		market = new ModelMarket();
	}

	// 测试初始设置
	function testInitialSettings() public {
		assertEq(market.admin(), admin);
		assertEq(market.commissionReceiver(), admin);
		assertEq(market.commissionRate(), 500); // 5%
	}

	// 测试管理员功能
	function testAdminFunctions() public {
		// 测试设置佣金比率
		market.setCommissionRate(1000); // 设置为 10%
		assertEq(market.commissionRate(), 1000);

		// 测试设置佣金接收者
		market.setCommissionReceiver(commissionReceiver);
		assertEq(market.commissionReceiver(), commissionReceiver);

		// 测试转移管理员权限
		market.transferAdmin(user1);
		assertEq(market.admin(), user1);

		// 测试非管理员无法调用管理员函数
		vm.startPrank(user2);
		vm.expectRevert("Only admin can set commission rate");
		market.setCommissionRate(2000);
		vm.stopPrank();
	}

	// 测试注册模型
	function testRegisterModel() public {
		vm.startPrank(user1);

		uint modelId = market.registerModel(
			"Test Model",
			"Description",
			1 ether,
			"ipfs://dataLink",
			"ipfs://readmeLink"
		);

		assertEq(modelId, 0); // 第一个模型 ID 应为 0

		// 验证模型详细信息
		ModelMarket.Model memory model = market.getModelDetails(modelId);
		assertEq(model.owner, user1);
		assertEq(model.name, "Test Model");
		assertEq(model.description, "Description");
		assertEq(model.price, 1 ether);
		assertEq(model.dataLink, "ipfs://dataLink");
		assertEq(model.isPublished, true);

		// 测试重复名称会失败
		vm.expectRevert("Model name already exists");
		market.registerModel(
			"Test Model",
			"Another description",
			2 ether,
			"ipfs://anotherDataLink",
			"ipfs://anotherReadmeLink"
		);

		vm.stopPrank();
	}

	// 测试购买模型
	function testPurchaseModel() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Paid Model",
			"Paid model description",
			1 ether,
			"ipfs://paidmodel",
			"ipfs://readme"
		);

		// 检查初始账户余额
		uint initialSellerBalance = user1.balance;
		uint initialCommissionReceiverBalance = admin.balance; // 初始管理员也是佣金接收者

		// user2购买模型
		vm.prank(user2);
		market.purchaseModel{ value: 1 ether }(modelId);

		// 验证账户余额变化
		uint commissionAmount = (1 ether * 500) / 10000; // 5%佣金
		uint sellerAmount = 1 ether - commissionAmount;

		assertEq(user1.balance, initialSellerBalance + sellerAmount);
		assertEq(
			admin.balance,
			initialCommissionReceiverBalance + commissionAmount
		);

		// 验证购买记录
		assertTrue(market.hasAccess(modelId, user2));

		// 测试重复购买会失败
		vm.expectRevert("Already purchased");
		vm.prank(user2);
		market.purchaseModel{ value: 1 ether }(modelId);
	}

	// 测试免费模型
	function testFreeModel() public {
		// 创建免费模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Free Model",
			"Free model description",
			0,
			"ipfs://freemodel",
			"ipfs://readme"
		);

		// 用户不花钱获取免费模型
		vm.prank(user2);
		market.purchaseModel(modelId);

		// 验证访问权限
		assertTrue(market.hasAccess(modelId, user2));
	}

	// 测试下架模型
	function testUnpublishModel() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Model To Unpublish",
			"Description",
			1 ether,
			"ipfs://dataLink",
			"ipfs://readmeLink"
		);

		// 下架模型
		vm.prank(user1);
		market.unpublishModel(modelId);

		// 验证模型状态
		ModelMarket.Model memory model = market.getModelDetails(modelId);
		assertEq(model.isPublished, false);

		// 验证名称可以重用
		assertFalse(market.isModelNameUsed("Model To Unpublish"));

		// 验证无法购买已下架模型
		vm.prank(user2);
		vm.expectRevert("Model not available");
		market.purchaseModel{ value: 1 ether }(modelId);
	}

	// 测试模型访问权限
	function testModelAccess() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Access Test Model",
			"Description",
			1 ether,
			"ipfs://secretdata",
			"ipfs://readme"
		);

		// 非所有者和未购买者不能看到数据链接
		vm.prank(user2);
		ModelMarket.Model memory modelForNonOwner = market.getModelDetails(modelId);
		assertEq(modelForNonOwner.dataLink, "");

		// 所有者可以看到完整信息
		vm.prank(user1);
		ModelMarket.Model memory modelForOwner = market.getModelDetails(modelId);
		assertEq(modelForOwner.dataLink, "ipfs://secretdata");

		// 购买后可以看到完整信息
		vm.prank(user2);
		market.purchaseModel{ value: 1 ether }(modelId);

		vm.prank(user2);
		ModelMarket.Model memory modelForBuyer = market.getModelDetails(modelId);
		assertEq(modelForBuyer.dataLink, "ipfs://secretdata");
	}

	// 测试获取模型列表
	function testGetAllModels() public {
		// 创建几个模型
		vm.startPrank(user1);
		uint model1 = market.registerModel(
			"Model 1",
			"Desc 1",
			1 ether,
			"ipfs://data1",
			"ipfs://readme1"
		);
		uint model2 = market.registerModel(
			"Model 2",
			"Desc 2",
			2 ether,
			"ipfs://data2",
			"ipfs://readme2"
		);
		vm.stopPrank();

		vm.prank(user2);
		uint model3 = market.registerModel(
			"Model 3",
			"Desc 3",
			0.5 ether,
			"ipfs://data3",
			"ipfs://readme3"
		);

		// 下架一个模型
		vm.prank(user1);
		market.unpublishModel(model2);

		// 获取所有可用模型
		uint[] memory allModels = market.getAllModels();

		// 应该只有两个模型
		assertEq(allModels.length, 2);
		assertEq(allModels[0], model1);
		assertEq(allModels[1], model3);
	}

	// 测试分页获取模型
	function testGetModelSummariesPaginated() public {
		// 创建多个模型
		vm.startPrank(user1);
		market.registerModel(
			"Model 1",
			"Desc 1",
			1 ether,
			"ipfs://data1",
			"ipfs://readme1"
		);
		market.registerModel(
			"Model 2",
			"Desc 2",
			2 ether,
			"ipfs://data2",
			"ipfs://readme2"
		);
		market.registerModel(
			"Model 3",
			"Desc 3",
			3 ether,
			"ipfs://data3",
			"ipfs://readme3"
		);
		market.registerModel(
			"Model 4",
			"Desc 4",
			4 ether,
			"ipfs://data4",
			"ipfs://readme4"
		);
		market.registerModel(
			"Model 5",
			"Desc 5",
			5 ether,
			"ipfs://data5",
			"ipfs://readme5"
		);
		vm.stopPrank();

		// 测试分页 - 第一页 (2个)
		(ModelMarket.ModelSummary[] memory page1, uint total1) = market
			.getModelSummariesPaginated(0, 2);
		assertEq(page1.length, 2);
		assertEq(total1, 5);
		assertEq(page1[0].name, "Model 1");
		assertEq(page1[1].name, "Model 2");

		// 测试分页 - 第二页 (2个)
		(ModelMarket.ModelSummary[] memory page2, uint total2) = market
			.getModelSummariesPaginated(2, 2);
		assertEq(page2.length, 2);
		assertEq(total2, 5);
		assertEq(page2[0].name, "Model 3");
		assertEq(page2[1].name, "Model 4");

		// 测试分页 - 第三页 (1个)
		(ModelMarket.ModelSummary[] memory page3, uint total3) = market
			.getModelSummariesPaginated(4, 2);
		assertEq(page3.length, 1);
		assertEq(total3, 5);
		assertEq(page3[0].name, "Model 5");
	}

	// 测试添加模型报告
	function testAddModelReport() public {
		// 注册模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Model With Report",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		// 添加报告
		vm.prank(user1);
		market.addModelReport(
			modelId,
			"report-001",
			95, // totalScore
			90, // languageScore
			85, // instructScore
			95, // codeScore
			80, // mathScore
			85, // reasoningScore
			90 // knowledgeScore
		);

		// 获取报告列表
		ModelMarket.Report[] memory reports = market.getModelReportList(modelId);
		assertEq(reports.length, 1);

		// 验证报告内容
		ModelMarket.Report memory report = market.getModelReport(modelId, 0);
		assertEq(report.reportId, "report-001");
		assertEq(report.executor, user1);
		assertEq(report.totalScore, 95);
		assertEq(report.languageScore, 90);

		// 非所有者无法添加报告
		vm.prank(user2);
		vm.expectRevert("Only owner can add report");
		market.addModelReport(modelId, "report-002", 80, 80, 80, 80, 80, 80, 80);
	}

	// 测试管理员更新数据链接
	function testUpdateModelDataLinkByAdmin() public {
		// 注册模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Admin Update Test",
			"Description",
			1 ether,
			"ipfs://olddata",
			"ipfs://oldreadme"
		);

		// 管理员更新链接
		bool success = market.updataModelDataLinkByAdminUser(
			modelId,
			"ipfs://newdata",
			"ipfs://newreadme"
		);
		assertTrue(success);

		// 验证更新
		vm.prank(user1); // 作为所有者查看
		ModelMarket.Model memory model = market.getModelDetails(modelId);
		assertEq(model.dataLink, "ipfs://newdata");
		assertEq(model.readmeLink, "ipfs://newreadme");

		// 非管理员无法更新
		vm.prank(user2);
		vm.expectRevert("Only admin can update data link");
		market.updataModelDataLinkByAdminUser(
			modelId,
			"ipfs://failedupdate",
			"ipfs://failedreadme"
		);
	}

	// 测试佣金计算和支付
	function testCommissionPayment() public {
		// 设置新的佣金接收者和佣金率
		market.setCommissionReceiver(commissionReceiver);
		market.setCommissionRate(1000); // 10%

		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Commission Test",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		uint initialSellerBalance = user1.balance;
		uint initialReceiverBalance = commissionReceiver.balance;

		// 购买模型
		vm.prank(user2);
		market.purchaseModel{ value: 1 ether }(modelId);

		// 计算预期的佣金和卖家收入
		uint expectedCommission = 0.1 ether; // 10%
		uint expectedSellerAmount = 0.9 ether;

		// 验证正确的金额被转移
		assertEq(user1.balance, initialSellerBalance + expectedSellerAmount);
		assertEq(
			commissionReceiver.balance,
			initialReceiverBalance + expectedCommission
		);
	}

	// 测试找零功能
	function testPurchaseWithChange() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Change Test Model",
			"Description",
			0.5 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		uint initialBalance = user2.balance;

		// 发送超额资金购买模型
		vm.prank(user2);
		market.purchaseModel{ value: 1 ether }(modelId);

		// 验证找零
		uint expectedSpent = 0.5 ether;
		uint expectedChange = 0.5 ether;
		uint expectedBalance = initialBalance - expectedSpent;

		assertEq(user2.balance, expectedBalance);
	}

	// 测试购买自己的模型限制
	function testCannotPurchaseOwnModel() public {
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Own Model",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		// 所有者尝试购买自己的模型
		vm.prank(user1);
		vm.expectRevert("Cannot purchase own model");
		market.purchaseModel{ value: 1 ether }(modelId);
	}

	// 测试资金不足的购买
	function testInsufficientFunds() public {
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Expensive Model",
			"Description",
			5 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		// 尝试以不足的资金购买
		vm.prank(user2);
		vm.expectRevert("Insufficient funds");
		market.purchaseModel{ value: 1 ether }(modelId);
	}

	// 测试获取用户的模型
	function testGetUserModels() public {
		// user1 创建两个模型
		vm.startPrank(user1);
		uint model1 = market.registerModel(
			"User Model 1",
			"Desc",
			1 ether,
			"ipfs://data1",
			"ipfs://readme1"
		);
		uint model2 = market.registerModel(
			"User Model 2",
			"Desc",
			2 ether,
			"ipfs://data2",
			"ipfs://readme2"
		);
		vm.stopPrank();

		// user2 创建一个模型
		vm.prank(user2);
		uint model3 = market.registerModel(
			"User2 Model",
			"Desc",
			3 ether,
			"ipfs://data3",
			"ipfs://readme3"
		);

		// 获取并验证 user1 的模型
		uint[] memory user1Models = market.getUserModels(user1);
		assertEq(user1Models.length, 2);
		assertEq(user1Models[0], model1);
		assertEq(user1Models[1], model2);

		// 获取并验证 user2 的模型
		uint[] memory user2Models = market.getUserModels(user2);
		assertEq(user2Models.length, 1);
		assertEq(user2Models[0], model3);
	}

	// 测试佣金比例上限
	function testCommissionRateLimit() public {
		// 尝试设置过高的佣金比例
		vm.expectRevert("Commission rate cannot exceed 30%");
		market.setCommissionRate(3100); // 31%

		// 设置最大允许的佣金比例
		market.setCommissionRate(3000); // 30%
		assertEq(market.commissionRate(), 3000);
	}

	// 测试无效的管理员地址
	function testInvalidAdminAddress() public {
		// 尝试将管理员设置为零地址
		vm.expectRevert("Invalid address");
		market.transferAdmin(address(0));
	}

	// 测试无效的佣金接收者地址
	function testInvalidCommissionReceiverAddress() public {
		// 尝试将佣金接收者设置为零地址
		vm.expectRevert("Invalid address");
		market.setCommissionReceiver(address(0));
	}

	// 测试空名称的模型注册
	function testEmptyModelName() public {
		vm.prank(user1);
		vm.expectRevert("Name cannot be empty");
		market.registerModel(
			"",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);
	}

	// 测试对已下架模型添加报告
	function testAddReportToUnpublishedModel() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Report Test Model",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		// 下架模型
		vm.prank(user1);
		market.unpublishModel(modelId);

		// 尝试添加报告
		vm.prank(user1);
		vm.expectRevert("Model not available");
		market.addModelReport(modelId, "report-fail", 80, 80, 80, 80, 80, 80, 80);
	}

	// 测试添加多个报告
	function testMultipleReports() public {
		// 创建模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Multiple Reports Model",
			"Description",
			1 ether,
			"ipfs://data",
			"ipfs://readme"
		);

		// 添加多个报告
		vm.startPrank(user1);
		market.addModelReport(modelId, "report-1", 90, 90, 90, 90, 90, 90, 90);
		market.addModelReport(modelId, "report-2", 85, 85, 85, 85, 85, 85, 85);
		market.addModelReport(modelId, "report-3", 95, 95, 95, 95, 95, 95, 95);
		vm.stopPrank();

		// 验证报告数量和内容
		ModelMarket.Report[] memory reports = market.getModelReportList(modelId);
		assertEq(reports.length, 3);
		assertEq(reports[0].reportId, "report-1");
		assertEq(reports[1].reportId, "report-2");
		assertEq(reports[2].reportId, "report-3");

		assertEq(reports[0].totalScore, 90);
		assertEq(reports[1].totalScore, 85);
		assertEq(reports[2].totalScore, 95);
	}

	// 测试负价格的情况
	function testNonNegativePrice() public {
		// 尝试注册负价格模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Free Model",
			"Description",
			0,
			"ipfs://data",
			"ipfs://readme"
		);

		// 验证模型注册成功，且价格为0
		ModelMarket.Model memory model = market.getModelDetails(modelId);
		assertEq(model.price, 0);
	}

	// 测试向免费模型发送资金的限制
	function testZeroPaymentForFreeModel() public {
		// 创建免费模型
		vm.prank(user1);
		uint modelId = market.registerModel(
			"Zero Payment Test",
			"Description",
			0,
			"ipfs://data",
			"ipfs://readme"
		);

		// 尝试向免费模型发送资金
		vm.prank(user2);
		vm.expectRevert("No payment required");
		market.purchaseModel{ value: 0.1 ether }(modelId);
	}
}
