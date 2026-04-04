"""LingmaFlow Harness Manager - Resilient agent resume mechanism."""

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import click


@dataclass
class ResumePoint:
    """接回點資訊，用於中斷後恢復執行。"""
    change_name: str
    next_task_id: str
    last_completed_id: str
    context: str
    failed_attempts: list[str]


class HarnessManager:
    """管理 tasks.json 和 PROGRESS.md 的讀寫，提供 agent 接回機制。"""
    
    def __init__(self, change_dir: Path):
        """初始化 HarnessManager。
        
        Args:
            change_dir: openspec change 的目錄路徑
        """
        self.change_dir = Path(change_dir).resolve()
        self.tasks_json_path = self.change_dir / 'tasks.json'
        self.progress_md_path = self.change_dir / 'PROGRESS.md'
        self.tasks_md_path = self.change_dir / 'tasks.md'
        
    def _run_git_command(self, message: str) -> None:
        """執行 git add 和 commit。
        
        Args:
            message: commit message
        """
        try:
            # Git add all
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.change_dir,
                check=True,
                capture_output=True
            )
            
            # Git commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.change_dir,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # Git 操作失敗時記錄但不拋出錯誤
            click.echo(f"⚠️  Git operation failed: {e}")
            click.echo("  Continuing anyway...")
    
    def parse_tasks_md(self) -> list[dict]:
        """解析 tasks.md 並轉換為 JSON 格式。
        
        Returns:
            task 字典列表
        """
        if not self.tasks_md_path.exists():
            return []
        
        tasks = []
        content = self.tasks_md_path.read_text(encoding='utf-8')
        
        # 解析 Markdown checkbox 格式
        # 匹配 - [x] 或 - [ ] 開頭的行（大小寫皆可）
        pattern = r'^-\s+\[([ xX])\]\s+(\d+(?:\.\d+)?(?:-\w+)?)\s+(.+)$'
        
        for line in content.splitlines():
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                done_char, task_id, description = match.groups()
                tasks.append({
                    'id': task_id,
                    'description': description.strip(),
                    'done': done_char.lower() == 'x',
                    'started_at': None,
                    'completed_at': None,
                    'notes': ''
                })
        
        return tasks
    
    def init_change(self, change_name: str, tasks: Optional[list[dict]] = None) -> None:
        """初始化一個 openspec change 的執行環境。
        
        Args:
            change_name: change 名稱
            tasks: 可選的 tasks 列表，如果未提供則從 tasks.md 轉換
        """
        # 如果未提供 tasks，則從 tasks.md 轉換
        if tasks is None:
            tasks = self.parse_tasks_md()
        
        # 建立 tasks.json
        with open(self.tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        
        # 建立空的 PROGRESS.md
        self.progress_md_path.write_text('', encoding='utf-8')
        
        # 備份 tasks.md（如果存在）
        if self.tasks_md_path.exists():
            backup_path = self.tasks_md_path.with_suffix('.md.bak')
            backup_path.write_text(self.tasks_md_path.read_text(encoding='utf-8'), encoding='utf-8')
        
        # 執行 git commit
        self._run_git_command(f'harness: init {change_name}')
        
        # 輸出統計
        done_count = sum(1 for t in tasks if t['done'])
        print(f"✓ Initialized harness for {change_name}")
        print(f"✓ tasks.json: {len(tasks)} tasks ({done_count} done)")
        print(f"✓ PROGRESS.md created")
        print(f"✓ git commit: harness: init {change_name}")
    
    def complete_task(self, task_id: str, notes: str = '') -> None:
        """完成一個 task 並記錄時間戳。
        
        Args:
            task_id: task ID
            notes: 備註資訊
        """
        if not self.tasks_json_path.exists():
            raise FileNotFoundError(f"tasks.json not found in {self.change_dir}")
        
        # 讀取 tasks.json
        with open(self.tasks_json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        # 找到對應的 task
        task_found = False
        task_description = ''
        for task in tasks:
            if task['id'] == task_id:
                task['done'] = True
                task['completed_at'] = self._get_utc_timestamp()
                task['notes'] = notes
                task_found = True
                task_description = task['description']
                break
        
        if not task_found:
            raise ValueError(f"Task {task_id} not found")
        
        # 寫回 tasks.json
        with open(self.tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        
        # 執行 git commit
        self._run_git_command(f'task({task_id}): {task_description}')
        
        print(f"✓ task {task_id} marked done")
        print(f"✓ git commit: task({task_id}): {task_description}")
    
    def _get_utc_timestamp(self) -> str:
        """獲取 UTC 時間戳。
        
        Returns:
            ISO 8601 格式的 UTC 時間戳
        """
        from datetime import timezone
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def log_session(
        self,
        completed: list[str],
        leftover: str,
        failed_attempts: list[str],
        next_step: str
    ) -> None:
        """記錄 session 到 PROGRESS.md。
                
        Args:
            completed: 完成的 task IDs 列表
            leftover: 遺留的任務狀態描述
            failed_attempts: 失敗的嘗試列表
            next_step: 下一步指示
        """
        timestamp = self._get_utc_timestamp()[:16].replace('T', ' ')
        
        # 建立 session 內容
        session_content = f"## Session {timestamp}\n\n"
        session_content += f"完成：task {', '.join(completed)}\n\n"
        session_content += f"遺留：{leftover}\n\n"
        session_content += f"失敗記錄：{'; '.join(failed_attempts) if failed_attempts else '無'}\n\n"
        session_content += f"下一步：{next_step}\n\n"
        session_content += "---\n\n"
        
        # 追加到 PROGRESS.md
        with open(self.progress_md_path, 'a', encoding='utf-8') as f:
            f.write(session_content)
        
        # 執行 git commit
        self._run_git_command('progress: session log')
        
        print(f"✓ Session logged to PROGRESS.md")
        print(f"✓ git commit: progress: session log")
    
    def get_resume_point(self) -> ResumePoint:
        """獲取接回點資訊。
        
        Returns:
            ResumePoint 物件
        """
        if not self.tasks_json_path.exists():
            raise FileNotFoundError(f"tasks.json not found in {self.change_dir}")
        
        # 讀取 tasks.json
        with open(self.tasks_json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        # 找到下一個未完成的 task
        next_task_id = None
        next_task_index = -1
        
        for i, task in enumerate(tasks):
            if not task['done'] and next_task_id is None:
                next_task_id = task['id']
                next_task_index = i
                break
        
        # 如果所有 task 都完成了
        if next_task_id is None:
            change_name = self.change_dir.name
            return ResumePoint(
                change_name=change_name,
                next_task_id='ALL_DONE',
                last_completed_id=tasks[-1]['id'] if tasks else 'none',
                context='',
                failed_attempts=[]
            )
        
        # 往回找前一個 done 的 task
        last_completed_id = 'none'
        for i in range(next_task_index - 1, -1, -1):
            if tasks[i]['done']:
                last_completed_id = tasks[i]['id']
                break
        
        # 讀取 PROGRESS.md 的最後一個 session
        context = ''
        failed_attempts = []
        
        if self.progress_md_path.exists() and self.progress_md_path.stat().st_size > 0:
            content = self.progress_md_path.read_text(encoding='utf-8')
            
            # 解析最後一個 session
            sessions = re.split(r'^## Session ', content, flags=re.MULTILINE)
            if len(sessions) > 1:
                last_session = sessions[-1].strip()
                
                # 提取遺留資訊
                leftover_match = re.search(r'遺留：(.+?)(?=\n\n|\n---|$)', last_session, re.DOTALL)
                if leftover_match:
                    context = leftover_match.group(1).strip()
                
                # 提取失敗記錄
                failed_match = re.search(r'失敗記錄：(.+?)(?=\n\n|\n---|$)', last_session, re.DOTALL)
                if failed_match:
                    failed_text = failed_match.group(1).strip()
                    if failed_text != '無':
                        failed_attempts = [f.strip() for f in failed_text.split(';')]
        
        # 獲取 change name（從目錄名）
        change_name = self.change_dir.name
        
        return ResumePoint(
            change_name=change_name,
            next_task_id=next_task_id,
            last_completed_id=last_completed_id,
            context=context,
            failed_attempts=failed_attempts
        )
    
    def generate_startup_brief(self) -> str:
        """生成接回指令字串。
        
        Returns:
            純文字格式的接回指令
        """
        resume_point = self.get_resume_point()
        
        brief = "═══════════════════════════════\n"
        brief += "RESUME BRIEF\n"
        brief += "═══════════════════════════════\n\n"
        brief += f"Change: {resume_point.change_name}\n"
        brief += f"Resume from: task {resume_point.next_task_id}\n"
        brief += f"Last completed: task {resume_point.last_completed_id}\n\n"
        
        if resume_point.context or resume_point.failed_attempts:
            brief += "Context from last session:\n"
            if resume_point.context:
                brief += f"- {resume_point.context}\n"
            if resume_point.failed_attempts:
                for attempt in resume_point.failed_attempts:
                    brief += f"- {attempt}\n"
            brief += "\n"
        
        brief += "Startup sequence:\n"
        brief += "1. git log --oneline -10\n"
        brief += "2. cat PROGRESS.md\n"
        brief += "3. cat tasks.json | python3 -c \"import json,sys; [print(t['id'],t['description']) for t in json.load(sys.stdin) if not t['done']]\"\n"
        brief += f"4. 從 task {resume_point.next_task_id} 繼續\n"
        brief += "═══════════════════════════════\n"
        
        return brief
    
    def get_status(self) -> dict:
        """獲取當前 change 的狀態摘要。
        
        Returns:
            包含進度資訊的字典
        """
        if not self.tasks_json_path.exists():
            return {'error': 'tasks.json not found'}
        
        # 讀取 tasks.json
        with open(self.tasks_json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        total = len(tasks)
        done = sum(1 for t in tasks if t['done'])
        percentage = (done / total * 100) if total > 0 else 0
        
        # 找到當前 task
        current_task = None
        for task in tasks:
            if not task['done']:
                current_task = task['id']
                break
        
        # 獲取最後 session 時間
        last_session = 'N/A'
        if self.progress_md_path.exists() and self.progress_md_path.stat().st_size > 0:
            content = self.progress_md_path.read_text(encoding='utf-8')
            sessions = re.findall(r'^## Session (\d{4}-\d{2}-\d{2} \d{2}:\d{2})', content, re.MULTILINE)
            if sessions:
                last_session = sessions[-1]
        
        return {
            'change_name': self.change_dir.name,
            'total': total,
            'done': done,
            'percentage': percentage,
            'current_task': current_task,
            'last_session': last_session
        }
