'use client';

import React from 'react';
import { ConfigProvider, theme } from 'antd';

const ThemeProvider = ({ children }: { children: React.ReactNode }) => (
  <ConfigProvider
    theme={{
      // 1. 单独使用暗色算法
      algorithm: theme.darkAlgorithm,

      // 2. 组合使用暗色算法与紧凑算法
      // algorithm: [theme.darkAlgorithm, theme.compactAlgorithm],
    }}
  >
    {children}
  </ConfigProvider>
);

export default ThemeProvider;