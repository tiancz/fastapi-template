import {
  Container,
  EmptyState,
  Flex,
  Heading,
  Table,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { KnowledgeBaseService } from "@/client"
import { KnowledgeBaseActionsMenu } from "@/components/Common/KnowledgeBaseActionsMenu"
import AddKnowledgeBase from "@/components/KnowledgeBase/AddKnowledgeBase"
import PendingItems from "@/components/Pending/PendingItems"
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx"

const knowledgeBasesSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 5

function getKnowledgeBasesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      KnowledgeBaseService.readKnowledgeBases({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["knowledgeBases", { page }],
  }
}

export const Route = createFileRoute("/_layout/knowledgeBase")({
  component: KnowledgeBase,
  validateSearch: (search) => knowledgeBasesSearchSchema.parse(search),
})

function KnowledgeBasesTable() {
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getKnowledgeBasesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const knowledgeBases = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  if (isLoading) {
    return <PendingItems />
  }

  if (knowledgeBases.length === 0) {
    return (
      <EmptyState.Root>
        <EmptyState.Content>
          <EmptyState.Indicator>
            <FiSearch />
          </EmptyState.Indicator>
          <VStack textAlign="center">
            <EmptyState.Title>You don't have any knowledge bases yet</EmptyState.Title>
            <EmptyState.Description>
              Add a new knowledge base to get started
            </EmptyState.Description>
          </VStack>
        </EmptyState.Content>
      </EmptyState.Root>
    )
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Name</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Description</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {knowledgeBases?.map((knowledgeBase) => (
            <Table.Row key={knowledgeBase.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell truncate maxW="sm">
                {knowledgeBase.id}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {knowledgeBase.name}
              </Table.Cell>
              <Table.Cell
                color={!knowledgeBase.description ? "gray" : "inherit"}
                truncate
                maxW="30%"
              >
                {knowledgeBase.description || "N/A"}
              </Table.Cell>
              <Table.Cell>
                <KnowledgeBaseActionsMenu item={knowledgeBase} />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  )
}

function KnowledgeBase() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        KnowledgeBases Management
      </Heading>
      <AddKnowledgeBase />
      <KnowledgeBasesTable />
    </Container>
  )
}
