// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import { Script, console } from "forge-std/Script.sol";
import { ModelMarket } from "../src/ModelMarket.sol";

contract ModelMarketScript is Script {
	ModelMarket public modelMarket;

	function setUp() public {}

	function run() public {
		vm.startBroadcast();

		modelMarket = new ModelMarket();

		vm.stopBroadcast();
	}
}
