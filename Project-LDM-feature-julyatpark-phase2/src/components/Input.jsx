import { forwardRef } from 'react';

/**
 * Pill-shaped text input matching the design system.
 * Pass `label` for an accessible label rendered above the input.
 */
const Input = forwardRef(function Input(
  { label, id, type = 'text', error, className = '', ...rest },
  ref
) {
  const inputId = id || rest.name || label?.toLowerCase().replace(/\s+/g, '-');
  return (
    <div className="flex flex-col gap-2">
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-text-secondary tracking-wide"
        >
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        type={type}
        className={`
          w-full
          bg-surface
          border border-border
          rounded-full
          px-5 py-3
          text-base text-text
          placeholder:text-text-muted
          transition-all duration-150
          focus:border-primary focus-ring-primary
          ${error ? 'border-error' : ''}
          ${className}
        `}
        {...rest}
      />
      {error && <p className="text-xs text-error pl-5">{error}</p>}
    </div>
  );
});

export default Input;
