import React, { useState, useEffect } from 'react';
import './CheckboxGroup.css';

interface CheckboxOption {
  id: string;
  label: string;
}

interface CheckboxGroupProps {
  options: CheckboxOption[];
  onSelectionChange?: (selectedIds: string[]) => void;
  className?: string;
  defaultSelectedIds?: string[];
}

const CheckboxGroup: React.FC<CheckboxGroupProps> = ({
  options,
  onSelectionChange,
  className,
  defaultSelectedIds = []
}) => {
  const [selectedIds, setSelectedIds] = useState<string[]>(defaultSelectedIds);

  // defaultSelectedIds가 변경되면 selectedIds 업데이트
  useEffect(() => {
    setSelectedIds(defaultSelectedIds);
  }, [defaultSelectedIds]);

  const handleToggle = (id: string) => {
    const newSelectedIds = selectedIds.includes(id)
      ? selectedIds.filter(selectedId => selectedId !== id)
      : [...selectedIds, id];
    
    setSelectedIds(newSelectedIds);
    
    if (onSelectionChange) {
      onSelectionChange(newSelectedIds);
    }
  };

  return (
    <div className={`checkbox-group ${className || ''}`}>
      {options.map((option) => (
        <label key={option.id} className="checkbox-item">
          <input
            type="checkbox"
            checked={selectedIds.includes(option.id)}
            onChange={() => handleToggle(option.id)}
            className="checkbox-input"
          />
          <span className="checkbox-custom">
            {selectedIds.includes(option.id) && (
              <svg
                className="checkbox-checkmark"
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M3 8L6 11L13 4"
                  stroke="var(--color-white)"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </span>
          <span className="checkbox-label">{option.label}</span>
        </label>
      ))}
    </div>
  );
};

export default CheckboxGroup;

