import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"
import { useNavigate } from "@tanstack/react-router"

import type { KnowledgeBasePublic } from "@/client"
import DeleteKnowledgeBase from "../KnowledgeBase/DeleteKnowledgeBase"
import EditKnowledgeBase from "../KnowledgeBase/EditKnowledgeBase"

interface KnowledgeBaseActionsMenuProps {
  item: KnowledgeBasePublic
}

export const KnowledgeBaseActionsMenu = ({ item }: KnowledgeBaseActionsMenuProps) => {
  const navigate = useNavigate()

  const handleViewDetail = () => {
    navigate({
      to: "/knowledgeBaseDetail",
      search: { id: item.id }
    })
  }

  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <button
          onClick={handleViewDetail}
          className="w-full text-left px-4 py-2 hover:bg-gray-100 flex items-center"
        >
          <span>查看详情</span>
        </button>
        <EditKnowledgeBase item={item} />
        <DeleteKnowledgeBase id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
