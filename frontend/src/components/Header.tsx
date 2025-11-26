import React from 'react';
import logo from '../assets/images/logo.png';
import './Header.css';

interface HeaderProps {
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ className }) => {
  return (
    <header className={`header ${className || ''}`}>
      <div className="header-content">
        <img src={logo} alt="Logo" className="header-logo" />
      </div>
    </header>
  );
};

export default Header;

