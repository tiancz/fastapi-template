import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { KnowledgeBasePublic } from "@/client"
import DeleteKnowledgeBase from "../KnowledgeBase/DeleteKnowledgeBase"
import EditKnowledgeBase from "../KnowledgeBase/EditKnowledgeBase"

interface KnowledgeBaseActionsMenuProps {
  item: KnowledgeBasePublic
}

export const KnowledgeBaseActionsMenu = ({ item }: KnowledgeBaseActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <EditKnowledgeBase item={item} />
        <DeleteKnowledgeBase id={item.id} />
      </MenuContent>
    </MenuRoot>
  )
}
