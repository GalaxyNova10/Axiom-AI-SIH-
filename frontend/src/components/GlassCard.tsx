import { motion } from 'motion/react';
import clsx from 'clsx';
import type { ReactNode, CSSProperties } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  glow?: boolean;
  hover?: boolean;
  delay?: number;
}

export default function GlassCard({ children, className, style, glow, hover = true, delay = 0 }: Props) {
  return (
    <motion.div
      className={clsx('card', glow && 'card-glow', className)}
      style={style}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : undefined}
    >
      {children}
    </motion.div>
  );
}

