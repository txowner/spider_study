
# 识别验证码

from PIL import Image
import subprocess


def cleanFile(filepath):
    # image = Image.open(filepath).convert('RGB')
    #
    # # 对图片进行阀值过滤,然后保存
    # image = image.point(lambda x: 0 if x<143 else 255)
    # image.save(new_filepath)

    #调用系统的tesseract 命令对图片进行OCR识别
    subprocess.run(["tesseract", filepath, "output"])

    # 打开文件读取 结果
    output_file = open('output.txt', 'r')
    print(output_file.read())
    output_file.close()


if __name__ == '__main__':
    cleanFile('captcha.jpg')
