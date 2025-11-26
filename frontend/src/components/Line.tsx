import React from 'react';
import './Line.css';

interface LineProps {
  className?: string;
}

const Line: React.FC<LineProps> = ({ className }) => {
  return (
    <hr className={`line ${className || ''}`} />
  );
};

export default Line;

