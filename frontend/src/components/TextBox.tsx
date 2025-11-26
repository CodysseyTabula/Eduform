import React from 'react';
import './TextBox.css';

interface TextBoxProps {
  children?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const TextBox: React.FC<TextBoxProps> = ({ children, className, onClick }) => {
  return (
    <div 
      className={`text-box ${className || ''}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

export default TextBox;

