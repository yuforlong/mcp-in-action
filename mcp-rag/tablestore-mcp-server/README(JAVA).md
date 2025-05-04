# tablestore-mcp-server

A Tablestore Java MCP Server.

> [模型上下文协议（Model Context Protocol，MCP）](https://modelcontextprotocol.io/introduction)是一个开放协议，支持大型语言模型（LLM）应用程序与外部数据源及工具之间的无缝集成。
> 无论是开发AI驱动的集成开发环境（IDE）、增强聊天界面功能，还是创建定制化AI工作流，MCP均提供了一种标准化方案，
> 可将LLMs与其所需的关键背景信息高效连接。

这篇文章介绍如何基于Tablestore(表格存储)构建一个MCP服务，使用其向量和标量的混合检索，提供检索相关的 tool 能力。
# 本地运行

## 部署环境
1. 操作系统：Ubuntu:22.04
2. JAVA版本：jdk17
3. MAVEN版本：3.6.3

## 下载源码

1. 使用 `git clone` 将代码下载到本地。
2. 进入到该项目 java 源码的根目录

```bash
cd ./alibabacloud-tablestore-mcp-server/tablestore-java-mcp-server-rag
```

## 编译代码

代码需要 `jdk17` 版本以上进行构建，使用了 `mvn` 进行包和环境管理。

```bash
   # 安装jdk17 环境
   sudo apt update
   sudo apt install openjdk-17-jdk
   # 安装Maven
   sudo apt install maven
   # 确保 jdk17 环境（mvn或mvnw）
   mvn package -DskipTests
   # 或者执行以下命令（）
   ./mvnw package -DskipTests -s settings.xml
```

## 3.3 配置环境变量

代码里所有的配置是通过环境变量来实现的，出完整的变量见下方表格。 主要依赖的数据库 [Tablestore(表格存储)](https://www.aliyun.com/product/ots) 支持按量付费，使用该工具，表和索引都会自动创建，仅需要在控制台上申请一个实例即可。
> 备注：新用户可以免费试用Tablestore2个月，存储 50 G，预留 1 VCU 

| 变量名                          |                              必填                              |         含义         |                                                      默认值                                                       |
|------------------------------|:------------------------------------------------------------:|:------------------:|:--------------------------------------------------------------------------------------------------------------:|
| TABLESTORE_INSTANCE_NAME     | <span style="color:red; font-weight:bold;">**是(yes)**</span> |        实例名         |                                                       -                                                        |
| TABLESTORE_ENDPOINT          | <span style="color:red; font-weight:bold;">**是(yes)**</span> |       实例访问地址       |                                                       -                                                        |
| TABLESTORE_ACCESS_KEY_ID     | <span style="color:red; font-weight:bold;">**是(yes)**</span> |       秘钥 ID        |                                                       -                                                        |
| TABLESTORE_ACCESS_KEY_SECRET | <span style="color:red; font-weight:bold;">**是(yes)**</span> |     秘钥 SECRET      |                                                       -                                                        |


## Embedding
为了方便，这里不使用云服务的Embedding能力，而使用了内置的本地Embedding模型，这些模型都是可以应用生产的模型，示例代码仅支持了 [DeepJavaLibrary](https://djl.ai/) 上自带的Embedding模型，基本上都来自 Hugging Face，使用十分简单。

想用其它Embedding模型可以运行 `com.alicloud.openservices.tablestore.sample.service.EmbeddingService.listModels()` 方法查看支持的模型。

## 运行 MCP 服务

```bash
   # 阿里云账号或RAM用户的AccessKey ID。
   export TABLESTORE_ACCESS_KEY_ID=xx
   # 阿里云账号或RAM用户的AccessKey Secret。
   export TABLESTORE_ACCESS_KEY_SECRET=xx
   export TABLESTORE_ENDPOINT=xxx
   export TABLESTORE_INSTANCE_NAME=xxx

   # 示例
   export TABLESTORE_ACCESS_KEY_ID=LTAI5tD8oeSxz6YswAmRRCuM666
   export TABLESTORE_ACCESS_KEY_SECRET=mWjSeJBlGb0PQOZMkeUvKyeADFvf2m666
   export TABLESTORE_ENDPOINT=https://l01shhaguhcu.cn-hangzhou.ots.aliyuncs.com
   export TABLESTORE_INSTANCE_NAME=l01shhaguhcu
   
   java -jar target/tablestore-java-mcp-server-1.0-SNAPSHOT.jar
```



## 附录
### Ubuntu22.04 配置阿里云的maven仓库
在 Ubuntu 22.04 上配置阿里云的 Maven 仓库，主要是通过修改 Maven 的用户配置文件 `settings.xml` 来实现。这将把 Maven 默认连接的中央仓库或其他仓库的请求重定向到阿里云的镜像仓库，从而加快依赖下载速度。

用户级别的 `settings.xml` 文件通常位于用户主目录下的 `.m2` 文件夹中，即 `~/.m2/settings.xml`。如果这个文件不存在，你需要手动创建它。
1.  **打开终端。**

2.  **导航到 Maven 配置目录并检查 `settings.xml` 文件。**
    ```bash
    cd ~/.m2/
    ```
    如果你收到 "No such file or directory" 的错误，说明 `.m2` 文件夹不存在，需要先创建它：
    ```bash
    mkdir ~/.m2
    cd ~/.m2/
    ```
    然后检查 `settings.xml` 是否存在：
    ```bash
    ls settings.xml
    ```
    如果文件存在，建议先备份一下，以防修改出错：
    ```bash
    cp settings.xml settings.xml.bak
    ```

3.  **创建或编辑 `settings.xml` 文件。**
    使用你喜欢的文本编辑器打开或创建一个新的 `settings.xml` 文件。例如，使用 `nano` 或 `vim`：
    ```bash
    nano settings.xml
    # 或者
    vim settings.xml
    ```

4.  **添加或修改 `<mirrors>` 配置。**
    在 `settings.xml` 文件中，找到 `<mirrors>` 标签。如果不存在，需要手动添加。在 `<mirrors>` 标签内部，添加或修改一个 `<mirror>` 条目来指向阿里云仓库。

    以下是一个完整的 `settings.xml` 文件示例，其中包含了阿里云镜像配置。如果你的文件已存在其他内容，只需确保在 `<settings>` 标签内有 `<mirrors>` 标签，并在其中正确配置阿里云的 `<mirror>` 条目。

    ```xml
    <?xml version="1.0" encoding="UTF-8"?>
    <settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">

      <servers>
        </servers>

      <mirrors>
        <mirror>
          <id>aliyunmaven</id>
          <name>阿里云公共仓库</name>
          <url>https://maven.aliyun.com/repository/public</url>
          <mirrorOf>*</mirrorOf> </mirror>
      </mirrors>

      </settings>
    ```

    **关键部分解释:**

    * `<mirrors>`: 这是存放所有镜像配置的标签。
    * `<mirror>`: 定义一个具体的镜像。
    * `<id>`: 镜像的唯一标识符，自定义即可，例如 `aliyunmaven`。
    * `<name>`: 镜像的描述性名称。
    * `<url>`: 阿里云 Maven 仓库的地址。`https://maven.aliyun.com/repository/public` 是一个常用的公共仓库地址，它包含了中央仓库以及其他的常用仓库镜像。你也可以只镜像中央仓库，使用 `https://maven.aliyun.com/repository/central`。
    * `<mirrorOf>`: 指定这个镜像将替代哪些仓库。
        * `*`: 匹配所有远程仓库，会把所有对其他仓库的请求都重定向到阿里云仓库（除了 `<repositories>` 中定义了 `id` 与 `mirrorOf` 相同的仓库）。这是最常见和简单的配置，适用于大多数情况。
        * `central`: 只镜像 Maven 的中央仓库。
        * `repo1,repo2`: 镜像指定 id 的仓库。
        * `*,!repo1`: 镜像所有仓库，除了 id 为 `repo1` 的仓库。

    推荐使用 `<mirrorOf>*`，这样配置一次就能镜像所有仓库，包括中央仓库以及项目 pom 文件或 profile 中定义的其他仓库（除非有特殊配置排除）。

5.  **保存并关闭文件。**
    * 如果使用 `nano`，按 `Ctrl + X`，然后按 `Y` 确认保存，再按 `Enter` 确认文件名。
    * 如果使用 `vim`，按 `Esc` 键，然后输入 `:wq` 并按 `Enter`。

6.  **验证配置。**
    现在当你运行 Maven 命令（如 `mvn clean install` 或 `mvn package`）时，Maven 应该会从阿里云的仓库下载依赖。你可以观察 Maven 的输出日志，看它从哪个 URL 下载文件，或者在下载依赖时是否感觉速度变快。

通过以上步骤，你就成功地在 Ubuntu 22.04 上为你的 Maven 配置了阿里云仓库镜像。

### 为RAM用户赋予表格存储读写权限的操作步骤

以下是为RAM用户赋予表格存储读写权限的详细操作步骤，您可以根据实际需求选择使用默认系统策略或自定义策略进行授权。

---

#### **方法一：使用默认系统策略**

1. **创建RAM用户**  
   如果尚未创建RAM用户，请先完成此步骤：
   - 登录阿里云RAM控制台。
   - 在左侧导航栏，选择**身份管理 > 用户**。
   - 单击**创建用户**，设置基本信息（如登录名称、显示名称等）。
   - 在**访问方式**区域，选中**使用永久AccessKey访问**，单击**确定**。
   - 完成安全验证后，保存生成的AccessKey ID和AccessKey Secret。

2. **授予默认系统策略权限**  
   默认系统策略提供了对表格存储的常用权限配置，您可以根据需求选择以下策略之一：
   - **读写权限**：授予`AliyunOTSFullAccess`权限，允许执行所有表格存储的管理操作。
   - **只写权限**：授予`AliyunOTSWriteOnlyAccess`权限，允许执行写操作。
   - **只读权限**：授予`AliyunOTSReadOnlyAccess`权限，允许读取表格数据。

   具体操作如下：
   - 在RAM控制台的**用户**页面，找到目标RAM用户。
   - 单击右侧的**添加权限**。
   - 在**新增授权**面板的**权限策略**区域，搜索并选中目标策略（如`AliyunOTSFullAccess`）。
   - 单击**确认新增授权**。

---

#### **方法二：使用自定义策略**

1. **创建RAM用户**  
   同上，确保目标RAM用户已创建。

2. **创建自定义权限策略**  
   自定义策略允许您根据具体需求配置更细粒度的权限。例如，以下策略允许RAM用户对特定实例及其表执行所有操作：
   ```json
   {
     "Version": "1",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "ots:*",
         "Resource": "acs:ots:<region>:<account-id>:instance/<instance-name>*"
       }
     ]
   }
   ```
   操作步骤如下：
   - 在RAM控制台的左侧导航栏，选择**权限管理 > 权限策略**。
   - 单击**创建权限策略**，选择**脚本编辑**页签。
   - 根据实际需求编写策略脚本，单击**确定**。
   - 填写策略名称（如`CustomOTSPolicy`），并保存。

3. **为RAM用户授予自定义策略权限**  
   - 在RAM控制台的**用户**页面，找到目标RAM用户。
   - 单击右侧的**添加权限**。
   - 在**新增授权**面板的**权限策略**区域，搜索并选中已创建的自定义策略。
   - 单击**确认新增授权**。

---

#### **方法三：使用临时访问凭证**

1. **创建RAM角色及授权**  
   - 创建可信实体为阿里云账号的RAM角色（如`ramtestappwrite`用于写操作）。
   - 为角色创建自定义权限策略，例如：
     ```json
     {
       "Version": "1",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": "ots:*",
           "Resource": "acs:ots:<region>:<account-id>:instance/<instance-name>*"
         }
       ]
     }
     ```
   - 将策略绑定至对应的角色。

2. **为RAM用户授予假设角色权限**  
   - 创建一个RAM用户，用于扮演上述RAM角色。
   - 为RAM用户定义允许假设特定角色的自定义策略，例如：
     ```json
     {
       "Version": "1",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": "sts:AssumeRole",
           "Resource": "acs:ram::<account-id>:role/<role-name>"
         }
       ]
     }
     ```
   - 将该策略授权给RAM用户。

3. **获取临时访问凭证**  
   - 使用STS服务获取临时访问凭证。
   - 在SDK中通过设置`OTSClient`对象时传入`AccessKeyId`、`AccessKeySecret`和`SecurityToken`，即可使用临时凭证访问表格存储资源。

---

### **注意事项**
- **权限最小化原则**：建议根据实际需求授予最小范围的权限，避免过度授权。
- **AccessKey Secret保存**：RAM用户的AccessKey Secret仅在创建时显示，请及时保存并妥善保管。
- **临时凭证有效期**：使用STS临时访问凭证时，请注意凭证的有效期，过期后需重新获取。

以上步骤涵盖了为RAM用户赋予表格存储读写权限的多种方式，您可以根据实际场景选择最适合的方案。 



### 获取TABLESTORE_ACCESS_KEY_SECRET

`TABLESTORE_ACCESS_KEY_SECRET` 是用于访问阿里云表格存储（Tablestore）服务的访问密钥的一部分，属于长期访问凭证。获取该密钥的具体步骤如下：

1. **登录阿里云控制台**  
   首先，您需要登录到阿里云官网，并进入控制台。

2. **进入 AccessKey 管理页面**  
   在控制台中，点击右上角的用户头像，选择 **AccessKey 管理**，或者直接在搜索框中输入 **AccessKey** 进行跳转。

3. **创建或查看 AccessKey**  
   - 如果您尚未创建 AccessKey，可以点击 **创建 AccessKey** 按钮，系统会生成一组新的 `AccessKey ID` 和 `AccessKey Secret`。
   - 如果已有 AccessKey，可以直接查看并记录 `AccessKey Secret`。

4. **保存密钥信息**  
   **重要**：`AccessKey Secret` 只会在创建时显示一次，请务必妥善保存。如果丢失，需重新生成新的 AccessKey。

### 注意事项
- **安全性提醒**：`AccessKey Secret` 是敏感信息，请勿将其泄露或将代码中的密钥上传至公共仓库。
- **权限管理**：建议为不同的应用场景创建 

相关链接 
读取数据 | 表格存储 https://help.aliyun.com/zh/tablestore/developer-reference/read-data-by-using-java-sdk
数字人流媒体服务WebSDK | 虚拟数字人 https://help.aliyun.com/zh/avatar/avatar/developer-reference/aliyunavatarsdk-for-web
配置访问凭证 | 表格存储 https://help.aliyun.com/zh/tablestore/developer-reference/tablestore-python-configure-access-credentials
配置访问凭证 | 表格存储 https://help.aliyun.com/zh/tablestore/developer-reference/tablestore-go-configure-access-credentials
映射富化函数 | 日志服务 https://help.aliyun.com/zh/sls/user-guide/mapping-and-enrichment-functions
配置访问凭证 | 表格存储 https://help.aliyun.com/zh/tablestore/developer-reference/tablestore-java-configure-access-credentials



### 获取 `TABLESTORE_ENDPOINT`


1. **登录表格存储控制台**  
   首先，登录阿里云官网，并进入表格存储（Tablestore）控制台。

2. **选择实例**  
   在控制台页面上方，选择资源组和地域后，进入 **概览** 页面。单击目标实例的别名或在 **操作** 列中单击 **实例管理**。

3. **查看实例访问地址**  
   在 **实例详情** 页签中，您可以找到实例的名称和访问地址（Endpoint）。该地址是表格存储服务的接入点，用于应用程序与表格存储实例之间的通信。

4. **确认网络类型**  
   - 如果您的应用与表格存储实例在同一地域，可以选择 **VPC地址** 或 **公网地址**。
   - 如果您的应用与表格存储实例不在同一地域，则需要使用 **公网地址**。

   **重要提示**：新创建的表格存储实例默认不启用公网访问功能。如果您需要通过公网访问实例，请在 **实例管理 > 网络管理** 页面中，选中 **允许网络类型** 中的 **公网**，并单击 **设置** 保存配置。

5. **记录 Endpoint**  
   将获取到的访问地址（Endpoint）记录下来，作为 `TABLESTORE_ENDPOINT` 的值。

### 示例格式
`TABLESTORE_ENDPOINT` 的值通常为以下格式：  
```
https://<实例名称>.<地域>.ots.aliyuncs.com
```

例如：
```
https://myinstance.cn-hangzhou.ots.aliyuncs.com
```

### 注意事项
- **安全性提醒**：确保 `TABLESTORE_ENDPOINT` 的值仅在安全环境中使用，避免泄露。
- **网络连通性**：如果使用 VPC 地址，请确保应用程序所在的环境与表格存储实例在同一个 VPC 内，否则可能会导致网络不通。

通过以上步骤，您可以成功获取 `TABLESTORE_ENDPOINT` 并将其用于相关配置。 


## 参考
1. 表格存储常见问题：https://help.aliyun.com/zh/tablestore/developer-reference/error-codes