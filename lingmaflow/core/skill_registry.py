"""
Skill Registry Module

This module provides skill discovery and query functionality for LingmaFlow,
enabling agents to dynamically load and use skills from the skills directory.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml


class MalformedSkillError(Exception):
    """Exception raised when a SKILL.md file cannot be parsed.
    
    This error occurs when the SKILL.md file is missing required fields
    or contains invalid YAML syntax that cannot be processed.
    """
    pass


@dataclass
class Skill:
    """Data class to hold skill information.
    
    Attributes:
        name: Unique identifier for the skill
        version: Version string (default: "1.0")
        triggers: List of trigger keywords that activate this skill
        priority: Priority level - high, normal, or low (default: "normal")
        content: The markdown body content of the SKILL.md file
        path: Path to the SKILL.md file
    """
    name: str
    triggers: List[str]
    content: str
    path: Path
    version: str = "1.0"
    priority: str = "normal"


class SkillRegistry:
    """Registry for managing and querying skills.
    
    This class provides methods to scan a directory for skills,
    load them, and query by name or keyword.
    
    Attributes:
        skills_dir: Path to the directory containing skill subdirectories
        skills: List of loaded Skill objects
    """
    
    def __init__(self, skills_dir: Path):
        """Initialize the SkillRegistry.
        
        Args:
            skills_dir: Path to the directory containing skill subdirectories
        """
        self.skills_dir = skills_dir
        self.skills: List[Skill] = []
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from SKILL.md content.
        
        Args:
            content: The full content of a SKILL.md file
            
        Returns:
            Dictionary with parsed frontmatter fields
            
        Raises:
            MalformedSkillError: If YAML syntax is invalid
        """
        # Check if content starts with frontmatter delimiter
        if not content.strip().startswith('---'):
            return {}
        
        # Split content into frontmatter and body
        parts = content.split('---', 2)
        if len(parts) < 2:
            raise MalformedSkillError("Invalid frontmatter format - missing closing '---'")
        
        frontmatter_str = parts[1].strip()
        
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter if frontmatter else {}
        except yaml.YAMLError as e:
            raise MalformedSkillError(f"Invalid YAML syntax in frontmatter: {e}")
    
    def _parse_skill_file(self, path: Path) -> Skill:
        """Parse a SKILL.md file and return a Skill object.
        
        Args:
            path: Path to the SKILL.md file
            
        Returns:
            Parsed Skill object
            
        Raises:
            MalformedSkillError: If required fields are missing or invalid
        """
        # Read file content
        content = path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        
        # Validate required fields
        if 'name' not in frontmatter or not frontmatter.get('name'):
            raise MalformedSkillError("Missing required field: 'name'")
        
        if 'triggers' not in frontmatter:
            raise MalformedSkillError("Missing required field: 'triggers'")
        
        if not isinstance(frontmatter['triggers'], list):
            raise MalformedSkillError("Field 'triggers' must be a list")
        
        # Extract body (content after frontmatter)
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            body = parts[2].strip() if len(parts) > 2 else ""
        else:
            body = content.strip()
        
        # Create Skill object with defaults for optional fields
        return Skill(
            name=frontmatter['name'],
            version=frontmatter.get('version', '1.0'),
            triggers=frontmatter['triggers'],
            priority=frontmatter.get('priority', 'normal'),
            content=body,
            path=path
        )
    
    def scan(self) -> List[Skill]:
        """Scan the skills directory and load all SKILL.md files.
        
        Returns:
            List of loaded Skill objects
            
        Raises:
            MalformedSkillError: If any SKILL.md file is malformed
        """
        self.skills = []
        
        if not self.skills_dir.exists():
            return self.skills
        
        # Scan immediate subdirectories only (not recursive)
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                skill_file = item / "SKILL.md"
                if skill_file.exists():
                    skill = self._parse_skill_file(skill_file)
                    self.skills.append(skill)
        
        return self.skills
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by its exact name.
        
        Args:
            name: The exact name of the skill to retrieve
            
        Returns:
            The Skill object if found, None otherwise
        """
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None
    
    def find(self, keyword: str) -> List[Skill]:
        """Find skills by keyword matching against triggers.
        
        Args:
            keyword: The keyword to search for
            
        Returns:
            List of matching Skill objects
        """
        matches = []
        keyword_lower = keyword.lower()
        
        for skill in self.skills:
            for trigger in skill.triggers:
                if keyword_lower in trigger.lower():
                    matches.append(skill)
                    break  # Add each skill only once
        
        return matches
    
    def list(self) -> List[str]:
        """List names of all loaded skills.
        
        Returns:
            List of skill names
        """
        return [skill.name for skill in self.skills]
