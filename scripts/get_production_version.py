from re import search

if __name__ == "__main__":
    with open("docker-compose-production.yml", "r") as f:
        res = search(
            r"docker.idiap.ch/wenet/personal_context_builder:([^']+)", f.read()
        )
        if res is None:
            print("latest")
        else:
            print(res.group(1))
