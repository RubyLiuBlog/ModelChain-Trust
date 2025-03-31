export default [
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
      {
        internalType: "string",
        name: "_reportId",
        type: "string",
      },
      {
        internalType: "uint256",
        name: "_totalScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_languageScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_instructScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_codeScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_mathScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_reasoningScore",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_knowledgeScore",
        type: "uint256",
      },
    ],
    name: "addModelReport",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [],
    stateMutability: "nonpayable",
    type: "constructor",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "uint256",
        name: "modelId",
        type: "uint256",
      },
      {
        indexed: true,
        internalType: "address",
        name: "owner",
        type: "address",
      },
      {
        indexed: false,
        internalType: "string",
        name: "name",
        type: "string",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "price",
        type: "uint256",
      },
    ],
    name: "ModelListed",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "uint256",
        name: "modelId",
        type: "uint256",
      },
      {
        indexed: true,
        internalType: "address",
        name: "buyer",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "price",
        type: "uint256",
      },
    ],
    name: "ModelPurchased",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "uint256",
        name: "modelId",
        type: "uint256",
      },
      {
        indexed: true,
        internalType: "address",
        name: "owner",
        type: "address",
      },
    ],
    name: "ModelUnpublished",
    type: "event",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
    ],
    name: "purchaseModel",
    outputs: [],
    stateMutability: "payable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "string",
        name: "_name",
        type: "string",
      },
      {
        internalType: "string",
        name: "_description",
        type: "string",
      },
      {
        internalType: "uint256",
        name: "_price",
        type: "uint256",
      },
      {
        internalType: "string",
        name: "_dataLink",
        type: "string",
      },
      {
        internalType: "string",
        name: "_readmeLink",
        type: "string",
      },
    ],
    name: "registerModel",
    outputs: [
      {
        internalType: "uint256",
        name: "modelId",
        type: "uint256",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_rate",
        type: "uint256",
      },
    ],
    name: "setCommissionRate",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "_receiver",
        type: "address",
      },
    ],
    name: "setCommissionReceiver",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "_newAdmin",
        type: "address",
      },
    ],
    name: "transferAdmin",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
    ],
    name: "unpublishModel",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
      {
        internalType: "string",
        name: "_dataLink",
        type: "string",
      },
      {
        internalType: "string",
        name: "_readmeLink",
        type: "string",
      },
    ],
    name: "updataModelDataLinkByAdminUser",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [],
    name: "admin",
    outputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "commissionRate",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "commissionReceiver",
    outputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "getAllModels",
    outputs: [
      {
        internalType: "uint256[]",
        name: "",
        type: "uint256[]",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
    ],
    name: "getModelDetails",
    outputs: [
      {
        components: [
          {
            internalType: "uint256",
            name: "id",
            type: "uint256",
          },
          {
            internalType: "address",
            name: "owner",
            type: "address",
          },
          {
            internalType: "string",
            name: "name",
            type: "string",
          },
          {
            internalType: "string",
            name: "description",
            type: "string",
          },
          {
            internalType: "string",
            name: "dataLink",
            type: "string",
          },
          {
            internalType: "string",
            name: "readmeLink",
            type: "string",
          },
          {
            internalType: "uint256",
            name: "price",
            type: "uint256",
          },
          {
            internalType: "bool",
            name: "isPublished",
            type: "bool",
          },
          {
            components: [
              {
                internalType: "string",
                name: "reportId",
                type: "string",
              },
              {
                internalType: "address",
                name: "executor",
                type: "address",
              },
              {
                internalType: "uint256",
                name: "totalScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "languageScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "instructScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "codeScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "mathScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "reasoningScore",
                type: "uint256",
              },
              {
                internalType: "uint256",
                name: "knowledgeScore",
                type: "uint256",
              },
            ],
            internalType: "struct ModelMarket.Report[]",
            name: "reportList",
            type: "tuple[]",
          },
        ],
        internalType: "struct ModelMarket.Model",
        name: "",
        type: "tuple",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_reportId",
        type: "uint256",
      },
    ],
    name: "getModelReport",
    outputs: [
      {
        components: [
          {
            internalType: "string",
            name: "reportId",
            type: "string",
          },
          {
            internalType: "address",
            name: "executor",
            type: "address",
          },
          {
            internalType: "uint256",
            name: "totalScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "languageScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "instructScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "codeScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "mathScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "reasoningScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "knowledgeScore",
            type: "uint256",
          },
        ],
        internalType: "struct ModelMarket.Report",
        name: "",
        type: "tuple",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
    ],
    name: "getModelReportList",
    outputs: [
      {
        components: [
          {
            internalType: "string",
            name: "reportId",
            type: "string",
          },
          {
            internalType: "address",
            name: "executor",
            type: "address",
          },
          {
            internalType: "uint256",
            name: "totalScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "languageScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "instructScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "codeScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "mathScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "reasoningScore",
            type: "uint256",
          },
          {
            internalType: "uint256",
            name: "knowledgeScore",
            type: "uint256",
          },
        ],
        internalType: "struct ModelMarket.Report[]",
        name: "",
        type: "tuple[]",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_offset",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "_limit",
        type: "uint256",
      },
    ],
    name: "getModelSummariesPaginated",
    outputs: [
      {
        components: [
          {
            internalType: "uint256",
            name: "id",
            type: "uint256",
          },
          {
            internalType: "address",
            name: "owner",
            type: "address",
          },
          {
            internalType: "string",
            name: "name",
            type: "string",
          },
          {
            internalType: "string",
            name: "description",
            type: "string",
          },
          {
            internalType: "uint256",
            name: "price",
            type: "uint256",
          },
        ],
        internalType: "struct ModelMarket.ModelSummary[]",
        name: "summaries",
        type: "tuple[]",
      },
      {
        internalType: "uint256",
        name: "total",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "_user",
        type: "address",
      },
    ],
    name: "getUserModels",
    outputs: [
      {
        internalType: "uint256[]",
        name: "",
        type: "uint256[]",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "_modelId",
        type: "uint256",
      },
      {
        internalType: "address",
        name: "_user",
        type: "address",
      },
    ],
    name: "hasAccess",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "string",
        name: "_dataLink",
        type: "string",
      },
    ],
    name: "isDataLinkUsed",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "string",
        name: "_name",
        type: "string",
      },
    ],
    name: "isModelNameUsed",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    name: "models",
    outputs: [
      {
        internalType: "uint256",
        name: "id",
        type: "uint256",
      },
      {
        internalType: "address",
        name: "owner",
        type: "address",
      },
      {
        internalType: "string",
        name: "name",
        type: "string",
      },
      {
        internalType: "string",
        name: "description",
        type: "string",
      },
      {
        internalType: "string",
        name: "dataLink",
        type: "string",
      },
      {
        internalType: "string",
        name: "readmeLink",
        type: "string",
      },
      {
        internalType: "uint256",
        name: "price",
        type: "uint256",
      },
      {
        internalType: "bool",
        name: "isPublished",
        type: "bool",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    name: "purchases",
    outputs: [
      {
        internalType: "bool",
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    name: "userModels",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
];
