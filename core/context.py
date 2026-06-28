from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RegisterBank(BaseModel):
    registers: dict[str, Any] = Field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        self.registers[key] = value

    def get(self, key: str) -> Any:
        return self.registers.get(key)


class ExecutionContext(BaseModel):
    objective: str
    register_bank: RegisterBank = Field(default_factory=RegisterBank)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance_events: list[dict[str, Any]] = Field(default_factory=list)

    def add_provenance_event(self, event: dict[str, Any]) -> None:
        self.provenance_events.append(event)
