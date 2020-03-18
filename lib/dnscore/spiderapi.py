import simplejson
import subprocess



def main():
    target = "http://tutorabc.com.cn/"
    cmd = ["./crawlergo.exe", "-c", "./chrome-win/chrome", "-o", "json", target]
    rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = rsp.communicate()
	#  "--[Mission Complete]--"  是任务结束的分隔字符串
    result = simplejson.loads(output.decode().split("--[Mission Complete]--")[1])
    req_list = result["all_req_list"]
    print(req_list)


if __name__ == '__main__':
    main()