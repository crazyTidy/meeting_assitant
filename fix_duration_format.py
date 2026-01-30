"""Fix duration format to HH:MM:SS."""
import os

frontend_path = r'c:\Users\JK-T-004\Desktop\wuguipeng\meetting_assitant\meeting-assistant-frontend\src\views'

files_to_update = [
    os.path.join(frontend_path, 'MeetingDetailView.vue'),
    os.path.join(frontend_path, 'MeetingListView.vue')
]

old_function = '''const formatDuration = (seconds?: number): string => {
  if (!seconds) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  if (h > 0) return `${h}小时${m}分钟`
  return `${m}分钟`
}'''

new_function = '''const formatDuration = (seconds?: number): string => {
  if (!seconds) return '--'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  // Format as HH:MM:SS
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}'''

for file_path in files_to_update:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace formatDuration function
    if old_function in content:
        content = content.replace(old_function, new_function)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {os.path.basename(file_path)}')
    else:
        print(f'Function not found in {os.path.basename(file_path)}')

print('Done!')
