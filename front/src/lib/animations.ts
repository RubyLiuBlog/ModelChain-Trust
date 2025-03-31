// lib/animations.ts
import { Variants } from 'framer-motion';

/**
 * 页面元素进入动画
 */
export const fadeInUp: Variants = {
  initial: {
    y: 20,
    opacity: 0,
  },
  animate: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

/**
 * 页面元素渐入动画
 */
export const fadeIn: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.5,
    },
  },
};

/**
 * 卡片悬浮效果
 */
export const hoverScale: Variants = {
  initial: {},
  hover: {
    scale: 1.03,
    transition: {
      duration: 0.2,
      type: 'spring',
      stiffness: 300,
    },
  },
};

/**
 * 容器显示动画，带子元素级联效果
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

/**
 * 按钮点击效果
 */
export const buttonTap: Variants = {
  initial: {},
  tap: {
    scale: 0.97,
    transition: {
      duration: 0.1,
    },
  },
};

/**
 * 交易成功烟花效果配置
 */
export const confettiConfig = {
  angle: 90,
  spread: 360,
  startVelocity: 40,
  elementCount: 200,
  dragFriction: 0.12,
  duration: 4000,
  stagger: 3,
  width: "10px",
  height: "10px",
  colors: ["#a864fd", "#29cdff", "#78ff44", "#ff718d", "#fdff6a"],
};

/**
 * 抖动动画
 */
export const shake: Variants = {
  initial: {},
  animate: {
    x: [0, -10, 10, -10, 10, 0],
    transition: {
      duration: 0.5,
    },
  },
};

/**
 * 脉冲动画
 */
export const pulse: Variants = {
  initial: {},
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      repeatType: "reverse",
    },
  },
};

/**
 * 进度条动画
 */
export const progressBar: Variants = {
  initial: {
    width: 0,
  },
  animate: (value: number) => ({
    width: `${value}%`,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  }),
};

/**
 * 页面切换动画
 */
export const pageTransition = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.3,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * 模态框显示动画
 */
export const modalAnimation: Variants = {
  initial: {
    opacity: 0,
    scale: 0.9,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: 'backOut',
    },
  },
  exit: {
    opacity: 0,
    scale: 0.9,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * 图表数据加载动画
 */
export const chartAnimation: Variants = {
  initial: {
    opacity: 0,
    pathLength: 0,
  },
  animate: {
    opacity: 1,
    pathLength: 1,
    transition: {
      duration: 1.5,
      ease: 'easeInOut',
    },
  },
};

/**
 * 列表项删除动画
 */
export const listItemExit: Variants = {
  initial: {
    opacity: 1,
    height: 'auto',
  },
  exit: {
    opacity: 0,
    height: 0,
    transition: {
      opacity: { duration: 0.2 },
      height: { duration: 0.3, delay: 0.1 },
    },
  },
};