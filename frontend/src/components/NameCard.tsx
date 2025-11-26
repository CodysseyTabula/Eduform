import React from 'react';
import './NameCard.css';

interface NameCardProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const NameCard: React.FC<NameCardProps> = ({ 
  title, 
  description, 
  children, 
  className, 
  onClick 
}) => {
  return (
    <div 
      className={`name-card ${className || ''}`}
      onClick={onClick}
    >
      {title && <h3 className="name-card-title">{title}</h3>}
      {description && <p className="name-card-description">{description}</p>}
      {children}
    </div>
  );
};

export default NameCard;

