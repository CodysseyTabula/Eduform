import React from 'react';
import './Button.css';

interface ButtonProps {
  children: React.ReactNode;
  icon?: React.ReactNode;
  arrowDirection?: 'left' | 'right' | null;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  icon,
  arrowDirection,
  onClick,
  type = 'button',
  className
}) => {
  const renderIcon = () => {
    if (icon) {
      return <span className="button-icon">{icon}</span>;
    }
    
    if (arrowDirection === 'left') {
      return (
        <svg
          className="button-arrow"
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M7 1L2 6L7 11"
            stroke="var(--color-white)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    }
    
    if (arrowDirection === 'right') {
      return (
        <svg
          className="button-arrow"
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M5 1L10 6L5 11"
            stroke="var(--color-white)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      );
    }
    
    return null;
  };

  return (
    <button
      type={type}
      className={`button ${className || ''}`}
      onClick={onClick}
    >
      {renderIcon() && (
        <span className="button-icon-wrapper">
          {renderIcon()}
        </span>
      )}
      <span className="button-text">{children}</span>
    </button>
  );
};

export default Button;

