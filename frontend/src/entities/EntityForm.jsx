import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormHelperText,
  FormLabel,
  Input,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Textarea,
  VStack,
  useToast,
  Heading,
  Spinner,
  Center,
  FormErrorMessage,
  HStack,
  IconButton,
  Select,
  Switch,
  Text,
  Divider,
  Icon,
  Tooltip,
  Badge,
} from '@chakra-ui/react';
import { ArrowBackIcon, AddIcon, DeleteIcon } from '@chakra-ui/icons';
import { useNavigate, useParams, Link as RouterLink } from 'react-router-dom';

const API_URL = 'http://localhost:8081/entities';

// Tipi di campo supportati
const FIELD_TYPES = [
  { value: 'string', label: 'Testo' },
  { value: 'integer', label: 'Numero Intero' },
  { value: 'float', label: 'Numero Decimale' },
  { value: 'boolean', label: 'Booleano' },
  { value: 'date', label: 'Data' },
  { value: 'datetime', label: 'Data e Ora' },
];

// Componente per la riga del campo nella tabella
const FieldRow = ({
  field,
  index,
  onUpdate,
  onRemove,
  errors = {},
  availableEntities = []
}) => {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    onUpdate(index, {
      ...field,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <Tr>
      <Td px={2} py={3}>
        <FormControl isInvalid={!!errors[`field-${index}-name`]}>
          <Input
            name="field_name"
            value={field.field_name || ''}
            onChange={handleChange}
            placeholder="es: nome_utente"
            size="sm"
          />
          {errors[`field-${index}-name`] && (
            <Text color="red.500" fontSize="xs" mt={1}>
              {errors[`field-${index}-name`]}
            </Text>
          )}
        </FormControl>
      </Td>
      
      <Td px={2} py={3}>
        <FormControl>
          <Select
            name="field_type"
            value={field.field_type || 'string'}
            onChange={handleChange}
            size="sm"
          >
            {FIELD_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </FormControl>
      </Td>

      <Td px={2} py={3}>
        <FormControl>
          <Select
            name="field_entity_id"
            value={field.field_entity_id || ''}
            onChange={handleChange}
            size="sm"
            placeholder="Seleziona entità"
          >
            {availableEntities.map((entity) => (
              <option key={entity.id} value={entity.id}>
                {entity.name}
              </option>
            ))}
          </Select>
        </FormControl>
      </Td>
      
      <Td px={2} py={3} textAlign="center">
        <Switch
          name="required"
          isChecked={field.required !== false}
          onChange={handleChange}
          colorScheme="blue"
        />
      </Td>
      
      <Td px={2} py={3}>
        <Input
          name="default_value"
          value={field.default_value || ''}
          onChange={handleChange}
          placeholder="Default"
          size="sm"
        />
      </Td>
      
      <Td px={2} py={3} textAlign="center">
        <IconButton
          icon={<DeleteIcon />}
          size="sm"
          variant="ghost"
          colorScheme="red"
          onClick={onRemove}
          aria-label="Rimuovi campo"
        />
      </Td>
    </Tr>
  );
};

const EntityForm = () => {
  const { id } = useParams();
  const isEditing = !!id;
  const navigate = useNavigate();
  const toast = useToast();
  
  const [loading, setLoading] = useState(isEditing);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    table_name: '',
    fields: []
  });
  const [errors, setErrors] = useState({});
  const [availableEntities, setAvailableEntities] = useState([]);
  
  // Fetch available entities for field types
  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error('Errore nel caricamento delle entità');
        }
        const data = await response.json();
        setAvailableEntities(data);
      } catch (error) {
        toast({
          title: 'Errore',
          description: 'Impossibile caricare le entità disponibili',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };
    fetchEntities();
  }, [toast]);
  
  // Aggiunge un nuovo campo vuoto
  const addField = () => {
    setFormData(prev => ({
      ...prev,
      fields: [
        ...prev.fields,
        { 
          field_name: '', 
          field_type: 'string', 
          field_entity_id: availableEntities[0]?.id || null,
          required: true 
        }
      ]
    }));
  };
  
  // Aggiorna un campo esistente
  const updateField = (index, updatedField) => {
    setFormData(prev => ({
      ...prev,
      fields: prev.fields.map((field, i) => 
        i === index ? updatedField : field
      )
    }));
  };
  
  // Rimuove un campo
  const removeField = (index) => {
    setFormData(prev => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index)
    }));
  };

  useEffect(() => {
    if (isEditing) {
      const fetchEntity = async () => {
        try {
          const response = await fetch(`${API_URL}/${id}`);
          if (!response.ok) {
            throw new Error('Errore nel caricamento dell\'entità');
          }
          const data = await response.json();
          
          // Converti i fields da oggetto a array
          const fieldsArray = Object.entries(data.fields || {}).map(([name, def]) => ({
            name,
            type: def.type,
            required: def.required !== false,
            default: def.default || ''
          }));
          
          setFormData({
            name: data.name,
            table_name: data.table_name,
            fields: fieldsArray,
          });
        } catch (error) {
          toast({
            title: 'Errore',
            description: error.message,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          navigate('/entities');
        } finally {
          setLoading(false);
        }
      };
      fetchEntity();
    }
  }, [id, isEditing, navigate, toast]);

  const validateForm = () => {
    const newErrors = {};
    const fieldNames = new Set();
    
    // Validazione nome entità
    if (!formData.name.trim()) {
      newErrors.name = 'Il nome è obbligatorio';
    }
    
    // Validazione nome tabella
    if (!formData.table_name.trim()) {
      newErrors.table_name = 'Il nome della tabella è obbligatorio';
    } else if (!/^[a-z][a-z0-9_]*$/.test(formData.table_name)) {
      newErrors.table_name = 'Il nome della tabella può contenere solo lettere minuscole, numeri e underscore, e deve iniziare con una lettera';
    }
    
    // Validazione campi
    if (formData.fields.length === 0) {
      newErrors.fields = 'Aggiungi almeno un campo';
    } else {
      formData.fields.forEach((field, index) => {
        // Nome campo univoco
        if (fieldNames.has(field.name)) {
          newErrors[`field-${index}-name`] = 'Nome campo già utilizzato';
        } else if (field.name) {
          fieldNames.add(field.name);
        }
        
        // Nome campo valido
        if (!field.name) {
          newErrors[`field-${index}-name`] = 'Il nome del campo è obbligatorio';
        } else if (!/^[a-z][a-z0-9_]*$/.test(field.name)) {
          newErrors[`field-${index}-name`] = 'Usa solo lettere minuscole, numeri e underscore, iniziando con una lettera';
        }
      });
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setIsSubmitting(true);
      
      console.log('FormData originale:', formData);
      
      // Assicuriamoci che fields sia sempre un array
      const fieldsArray = Array.isArray(formData.fields) 
        ? formData.fields 
        : [];
      
      // Mappatura dei campi nel formato richiesto dal backend
      const processedFields = fieldsArray.map(field => ({
        name: field.name || '',
        type: field.type || 'string',
        required: field.required !== false,
        ...(field.default !== undefined && { default: field.default })
      }));
      
      const dataToSend = {
        name: formData.name || '',
        table_name: formData.table_name || '',
        fields: processedFields
      };
      
      // Validazione di base
      if (!dataToSend.name.trim()) {
        throw new Error('Il nome dell\'entità è obbligatorio');
      }
      if (!dataToSend.table_name.trim()) {
        throw new Error('Il nome della tabella è obbligatorio');
      }
      if (dataToSend.fields.length === 0) {
        throw new Error('Aggiungi almeno un campo all\'entità');
      }

      console.log('Dati da inviare al server:', JSON.stringify(dataToSend, null, 2));
      
      const method = isEditing ? 'PUT' : 'POST';
      const url = isEditing ? `${API_URL}/${id}` : API_URL;
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataToSend),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || (isEditing ? 'Errore durante l\'aggiornamento' : 'Errore durante la creazione');
        throw new Error(errorMessage);
      }
      
      toast({
        title: 'Successo',
        description: isEditing ? 'Entità aggiornata con successo' : 'Entità creata con successo',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      navigate('/entities');
    } catch (error) {
      toast({
        title: 'Errore',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  if (loading) {
    return (
      <Center h="200px">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (loading) {
    return (
      <Center h="200px">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box p={5}>
      <HStack mb={5}>
        <IconButton
          as={RouterLink}
          to="/entities"
          icon={<ArrowBackIcon />}
          variant="ghost"
          aria-label="Torna indietro"
          mr={2}
        />
        <Heading as="h1" size="lg">
          {isEditing ? 'Modifica Entità' : 'Nuova Entità'}
        </Heading>
      </HStack>
      
      <Box maxW="800px">
        <form onSubmit={handleSubmit}>
          <VStack spacing={6}>
            <Box w="100%" p={6} borderWidth="1px" borderRadius="md">
              <VStack spacing={4}>
                <FormControl isInvalid={!!errors.name} isRequired>
                  <FormLabel>Nome Entità</FormLabel>
                  <Input
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="es: Utente"
                  />
                  <FormErrorMessage>{errors.name}</FormErrorMessage>
                </FormControl>
                
                <FormControl isInvalid={!!errors.table_name} isRequired>
                  <FormLabel>Nome Tabella nel Database</FormLabel>
                  <Input
                    name="table_name"
                    value={formData.table_name}
                    onChange={handleChange}
                    placeholder="es: utenti"
                    fontFamily="mono"
                  />
                  <FormHelperText>
                    Usa solo lettere minuscole, numeri e underscore, iniziando con una lettera
                  </FormHelperText>
                  <FormErrorMessage>{errors.table_name}</FormErrorMessage>
                </FormControl>
              </VStack>
            </Box>
            
            <Box w="100%" mt={6}>
              <HStack justify="space-between" align="center" mb={4}>
                <Heading size="md">Campi</Heading>
                <Button
                  leftIcon={<AddIcon />}
                  colorScheme="blue"
                  size="sm"
                  onClick={addField}
                >
                  Aggiungi Campo
                </Button>
              </HStack>
              
              {errors.fields && (
                <Text color="red.500" mb={4}>
                  {errors.fields}
                </Text>
              )}
              
              <Box 
                borderWidth="1px" 
                borderRadius="md" 
                overflowX="auto"
                bg="white"
              >
                <Table variant="simple" size="sm">
                  <Thead bg="gray.50">
                    <Tr>
                      <Th px={2} py={3} width="25%">Nome Campo</Th>
                      <Th px={2} py={3} width="25%">Tipo</Th>
                      <Th px={2} py={3} width="25%">Entità</Th>
                      <Th px={2} py={3} width="15%" textAlign="center">Obbligatorio</Th>
                      <Th px={2} py={3} width="25%">Valore Default</Th>
                      <Th px={2} py={3} width="10%" textAlign="center">Azioni</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {formData.fields.length === 0 ? (
                      <Tr>
                        <Td 
                          colSpan={5} 
                          textAlign="center" 
                          color="gray.500"
                          py={6}
                        >
                          <VStack spacing={2}>
                            <Text>Nessun campo definito</Text>
                            <Text fontSize="sm">Clicca su "Aggiungi Campo" per iniziare</Text>
                          </VStack>
                        </Td>
                      </Tr>
                    ) : (
                      formData.fields.map((field, index) => (
                        <FieldRow
                          key={index}
                          field={field}
                          index={index}
                          onUpdate={updateField}
                          onRemove={() => removeField(index)}
                          errors={errors}
                          availableEntities={availableEntities}
                        />
                      ))
                    )}
                  </Tbody>
                </Table>
              </Box>
              
              <Box mt={2}>
                <Text fontSize="xs" color="gray.500">
                  * I nomi dei campi devono iniziare con una lettera e possono contenere solo lettere minuscole, numeri e underscore
                </Text>
              </Box>
            </Box>
            
            <Divider my={4} />
            
            <HStack spacing={4} w="100%" justify="flex-end" pt={4}>
              <Button 
                as={RouterLink} 
                to="/entities" 
                variant="outline"
              >
                Annulla
              </Button>
              <Button 
                type="submit" 
                colorScheme="blue"
                isLoading={loading}
              >
                {isEditing ? 'Aggiorna Entità' : 'Crea Entità'}
              </Button>
            </HStack>
          </VStack>
        </form>
      </Box>
    </Box>
  );
};

export default EntityForm;
