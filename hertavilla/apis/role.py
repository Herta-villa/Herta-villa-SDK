from __future__ import annotations

from typing import List, Sequence

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Role, RoleColor, RolePermission

from pydantic import parse_obj_as


class RoleAPIMixin(_BaseAPIMixin):
    async def operate_member_to_role(
        self,
        villa_id: int,
        role_id: int,
        uid: int,
        is_add: bool = True,
    ) -> None:
        """向身份组操作用户，包括把用户添加到身份组或者从身份组删除用户

        Args:
            villa_id (int): 大别野 id
            role_id (int): 身份组 id
            uid (int): 用户 id
            is_add (bool, optional): 是否是添加用户. Defaults to True.
        """
        await self.base_request(
            "/operateMemberToRole",
            "POST",
            villa_id,
            data={"role_id": role_id, "uid": uid, "is_add": is_add},
        )

    async def create_member_role(
        self,
        villa_id: int,
        name: str,
        color: RoleColor,
        permissions: Sequence[RolePermission],
    ) -> int:
        """为大别野创建新的身份组，可以设置该身份组拥有的权限，并为身份组添加用户。

        Args:
            villa_id (int): 大别野 id
            name (str): 身份组名称
            color (RoleColor): 身份组颜色，可选项见 ``hertavilla.model.RoleColor``
            permissions (Sequence[RolePermission]): 权限列表，可选项见 ``hertavilla.model.RolePermission``

        Returns:
            int: 身份组 id
        """  # noqa: E501
        return int(
            (
                await self.base_request(
                    "/createMemberRole",
                    "POST",
                    villa_id,
                    data={
                        "name": name,
                        "color": color.value,
                        "permissions": [perm.value for perm in permissions],
                    },
                )
            )["id"],
        )

    async def edit_member_role(
        self,
        villa_id: int,
        id_: int,
        name: str,
        color: RoleColor,
        permissions: Sequence[RolePermission],
    ) -> None:
        """编辑身份组，可以修改身份组的名称、颜色和权限。

        Args:
            villa_id (int): 大别野 id
            id_ (int): 身份组 id
            name (str): 身份组名称
            color (RoleColor): 身份组颜色，可选项见 ``hertavilla.model.RoleColor``
            permissions (Sequence[RolePermission]): 权限列表，可选项见 ``hertavilla.model.RolePermission``
        """  # noqa: E501
        await self.base_request(
            "/editMemberRole",
            "POST",
            villa_id,
            data={
                "id": id_,
                "name": name,
                "color": color.value,
                "permissions": [perm.value for perm in permissions],
            },
        )

    async def delete_member_role(self, villa_id: int, id_: int) -> None:
        """删除身份组

        Args:
            villa_id (int): 大别野 id
            id_ (int): 身份组 id
        """
        await self.base_request(
            "/deleteMemberRole",
            "POST",
            villa_id,
            data={"id": id_},
        )

    async def get_member_role_info(self, villa_id: int, role_id: int) -> Role:
        """获取身份组信息

        Args:
            villa_id (int): 大别野 id
            role_id (int): 身份组 id

        Returns:
            Role: 身份组信息
        """
        return Role.parse_obj(
            (
                await self.base_request(
                    "/getMemberRoleInfo",
                    "GET",
                    villa_id,
                    params={"role_id": role_id},
                )
            )["role"],
        )

    async def get_villa_member_roles(self, villa_id: int) -> list[Role]:
        """获取大别野下所有身份组

        Args:
            villa_id (int): 大别野 id

        Returns:
            list[Role]: 身份组列表
        """
        return parse_obj_as(
            List[Role],
            (
                await self.base_request(
                    "/getVillaMemberRoles",
                    "GET",
                    villa_id,
                )
            )["list"],
        )
