import React from 'react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import {
  Box,
  VStack,
  HStack,
  Stack,
  Heading,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Button,
  Text,
  Link,
  IconButton,
  Icon
} from '@chakra-ui/react';

// Map of component types to their corresponding Chakra UI components
const componentMap = {
  box: Box,
  vstack: VStack,
  hstack: HStack,
  stack: Stack,
  heading: Heading,
  formcontrol: FormControl,
  formlabel: FormLabel,
  input: Input,
  inputgroup: InputGroup,
  inputrightelement: InputRightElement,
  button: Button,
  text: Text,
  link: Link,
  icon: Icon,
  iconbutton: IconButton,
};

/**
 * Maps a component type string to its corresponding Chakra UI component
 * @param {string} type - The component type from the layout JSON
 * @returns {React.ComponentType} The corresponding Chakra UI component
 */
export const getComponentByType = (type) => {
  if (!type) {
    console.warn('Component type is undefined');
    return null;
  }
  
  const component = componentMap[type.toLowerCase()];
  if (!component) {
    console.warn(`No component found for type: ${type}`);
    return null;
  }
  return component;
};

/**
 * Renders a component based on its type and props
 * @param {Object} componentData - The component data from the layout JSON
 * @param {string} key - Unique key for React rendering
 * @returns {React.ReactNode} The rendered component
 */
export const renderComponent = (componentData, key) => {
  if (!componentData) {
    console.warn('Component data is undefined');
    return null;
  }
  
  const { type, props = {}, children, content, ...restProps } = componentData;
  
  if (!type) {
    console.warn('Component data is missing type property', componentData);
    return null;
  }
  
  const Component = getComponentByType(type);
  if (!Component) {
    console.warn(`Could not find component for type: ${type}`);
    return null;
  }

  // Merge props and restProps (for backward compatibility)
  const allProps = { ...restProps, ...props, key };
  
  try {
    // Handle icon components
    if (type === 'icon' && componentData.component) {
      const IconComponent = {
        'ViewIcon': ViewIcon,
        'ViewOffIcon': ViewOffIcon
      }[componentData.component];
      
      if (!IconComponent) {
        console.warn(`Icon component not found: ${componentData.component}`);
        return null;
      }
      
      return <IconComponent {...allProps} />;
    }

    // Handle special cases for components with content
    if (content !== undefined) {
      return (
        <Component {...allProps}>
          {content}
        </Component>
      );
    }

    // Handle components with children
    if (children && children.length > 0) {
      return (
        <Component {...allProps}>
          {children.map((child, index) => 
            renderComponent(child, `${key}-${index}`)
          )}
        </Component>
      );
    }

    // Handle self-closing components
    return <Component {...allProps} />;
  } catch (error) {
    console.error(`Error rendering component ${type}:`, error);
    return null;
  }
};

export default {
  getComponentByType,
  renderComponent,
};
