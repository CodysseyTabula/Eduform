import React from 'react';
import './TabButton.css';

interface TabButtonProps {
  children: React.ReactNode;
  isSelected: boolean;
  onClick?: () => void;
  className?: string;
}

const TabButton: React.FC<TabButtonProps> = ({
  children,
  isSelected,
  onClick,
  className
}) => {
  return (
    <button
      type="button"
      className={`tab-button ${isSelected ? 'selected' : 'unselected'} ${className || ''}`}
      onClick={onClick}
    >
      <span className="tab-button-text">{children}</span>
    </button>
  );
};

export default TabButton;

