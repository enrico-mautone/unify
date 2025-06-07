import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Heading,
  useToast,
  Spinner,
  Center,
  IconButton,
  HStack
} from '@chakra-ui/react';
import { AddIcon, DeleteIcon, EditIcon } from '@chakra-ui/icons';
import { Link as RouterLink } from 'react-router-dom';

const API_URL = 'http://localhost:8081/entities';

const EntityList = () => {
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const toast = useToast();

  const fetchEntities = async () => {
    try {
      const response = await fetch(API_URL);
      if (!response.ok) {
        throw new Error('Errore nel caricamento delle entità');
      }
      const data = await response.json();
      setEntities(data);
    } catch (error) {
      toast({
        title: 'Errore',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Sei sicuro di voler eliminare questa entità? Questa azione è irreversibile.')) {
      return;
    }

    setDeletingId(id);
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Errore durante l\'eliminazione dell\'entità');
      }

      toast({
        title: 'Eliminazione completata',
        description: 'L\'entità è stata eliminata con successo',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Aggiorna la lista delle entità
      fetchEntities();
    } catch (error) {
      toast({
        title: 'Errore',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setDeletingId(null);
    }
  };

  useEffect(() => {
    fetchEntities();
  }, []);

  if (loading) {
    return (
      <Center h="200px">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box p={5}>
      <HStack justifyContent="space-between" mb={5}>
        <Heading as="h1" size="lg">Gestione Entità</Heading>
        <Button
          as={RouterLink}
          to="/entities/new"
          leftIcon={<AddIcon />}
          colorScheme="blue"
        >
          Nuova Entità
        </Button>
      </HStack>

      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Nome</Th>
              <Th>Tabella</Th>
              <Th>Azioni</Th>
            </Tr>
          </Thead>
          <Tbody>
            {entities.map((entity) => (
              <Tr key={entity.id}>
                <Td>{entity.id}</Td>
                <Td>{entity.name}</Td>
                <Td>{entity.table_name}</Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      as={RouterLink}
                      to={`/entities/edit/${entity.id}`}
                      icon={<EditIcon />}
                      size="sm"
                      colorScheme="blue"
                      aria-label="Modifica"
                    />
                    <IconButton
                      icon={deletingId === entity.id ? <Spinner size="sm" /> : <DeleteIcon />}
                      size="sm"
                      colorScheme="red"
                      aria-label="Elimina"
                      onClick={() => handleDelete(entity.id)}
                      isDisabled={deletingId === entity.id}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default EntityList;
