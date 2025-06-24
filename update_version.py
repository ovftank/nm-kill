import re
import sys


def update_version_info(version):
    version_parts = version.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')

    file_version = f"({','.join(version_parts)})"

    with open('version_info.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'filevers=\([^)]+\)',
                     f'filevers={file_version}', content)
    content = re.sub(r'prodvers=\([^)]+\)',
                     f'prodvers={file_version}', content)
    content = re.sub(
        r"StringStruct\(u'FileVersion', u'[^']+'\)", f"StringStruct(u'FileVersion', u'{version}')", content)
    content = re.sub(
        r"StringStruct\(u'ProductVersion', u'[^']+'\)", f"StringStruct(u'ProductVersion', u'{version}')", content)

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated version_info.txt: {version}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        version = sys.argv[1]
    else:
        with open('version.py', 'r') as f:
            content = f.read()
            match = re.search(
                r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                version = match.group(1)
            else:
                version = "1.0.0"

    update_version_info(version)
