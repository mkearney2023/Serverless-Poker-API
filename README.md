# Serverless Poker API

[Overview](#overview)
<br>
[Technology](#technology)
<br>
[Prerequisites](#prerequisites)
<br>
[Deployment](#deployment)
<br>
[Demonstration](#demonstration)
<br>
[API Reference](#api-reference)

## Overview

To get started, users first create an account and set a unique user identifier. From there, they have the option to either create a new lobby or join an existing one. It's possible for a user participate in multiple lobbies at once. When a game is not in progress, users in a lobby can buy in a certain number of chips and vote to either play a new game or exit the lobby.

If a majority of the users in a lobby vote to play a new game, the game will begin. During their turn, a user can choose to check, call, raise, or fold. The round ends when everyone checks, or when someone raises the bet and everyone else either calls, goes all in, or folds.  

In the first round, players can only view the two hole cards they were dealt. In the second round, they can view their hole cards and three of the five community cards on the table. In the third round, they can view their hole cards and four of the five community cards. In the fourth and final round, players can view their hole cards and all five community cards.

When the game ends, users can view all of the hole cards that were dealt and all five of the community cards. They are also given a summary of each user's best hand along with how these hands ranked against each other. The winner(s) are then determined automatically and the chips in the pot are distributed based on the cards that were dealt, the bets that were made, and the users who folded.

If the majority of users in a lobby vote to exit the lobby, the service will settle the debts in the fewest transactions possible, taking into account the number of chips bought in and the number of chips a user has at the end of the game. Users can view all incoming and outgoing debts on their account.

## Technology

**Terraform:**  Terraform is an open-source infrastructure as code (IaC) tool used to define and deploy cloud infrastructure in a safe, efficient, and reusable manner.  It is used to automate the provisioning and management of the API's infrastructure on AWS.

**AWS DynamoDB:**  AWS DynamoDB is a fast and scalable NoSQL database service used to store the API's data, including game state, player information, and game history.  It is capable of handling millions of requests per second and provides low-latency access to data.

**AWS Lambda:**  AWS Lambda is a serverless computing service used to execute the API's business logic and handle incoming requests from clients. It automatically scales to meet demand and only charges users for the actual compute time they consume.

**AWS API Gateway:**   AWS API Gateway is a fully managed service used to expose the API's functionality to the internet and route incoming requests to the appropriate Lambda function.


## Prerequisites

[AWS Account](https://aws.amazon.com/)
<br>
[Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

## Deployment

#### Clone the repository:
```
git clone https://github.com/mkearney2023/poker.git
```

#### Change into repository directory:
```
cd poker
```
#### Set your AWS credentials:
You can pass your AWS credentials to Terraform using one of the following methods:

1. Set the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` environment variables.

2. Use a shared credentials file located at `~/.aws/credentials`

3. Use a named profile in the shared credentials file and set the `AWS_PROFILE` environment variable.

4. Use the AWS CLI and run the `aws configure` command.

5. Use an IAM role if your code will be running on an EC2 instance.

#### Deploy the API:
```
make
```
After completing these steps, a new file, `url`, will be generated, containing the invoke URL of the REST API.

#### Stop the API, remove all AWS infrastructure, and delete generated files:
```
make clean
```

## Demonstration

Included in this repository is a simple Python console application, `demo.py`, that uses the file generated by Terraform, `url`, as an endpoint to demonstrate the functionality of the REST API. To run this application, you will need to have Python 3 installed along with the requests package from pip. You can then run the application from the command line by entering `python3 demo.py`. The demo application will send HTTP requests to the API endpoints and display the results to the console, allowing you to easily interact with the API and see how it works. This can be useful for testing and debugging the API, as well as for showcasing its capabilities to others.


## API Reference

#### View User Information
```
  GET /users/{user_id}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user to fetch |

Response:
```
{
    "id": "user1",
    "lobbies": [
        {
            "id": "lobby1"
        },
        {
            "id": "lobby2"
        },
        {
            "id": "lobby3"
        },
        {
            "id": "lobby4"
        }
    ],
    "debts": [
        {
            "id": "4240f823-1084-4eb0-8321-cba76ebd4ebe"
        },
        {
            "id": "af19a087-a3f2-4157-8900-0e64af4a6fcd"
        },
        {
            "id": "b9174399-371a-4ba5-9aa5-24d32f8faa45"
        }
    ]
}
```


#### View Lobby Information
```
  GET /users/{user_id}/lobbies/{lobby_id}
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user_id`      | `string` | **Required**. ID of user in lobby |
| `lobby_id`      | `string` | **Required**. ID of lobby to fetch |

Response:
```
{
    "id": "lobby1",
    "first_user": 1,
    "current_user": 1,
    "current_move": 0,
    "current_round": 4,
    "community_cards": [
        "TS",
        "8S",
        "QS",
        "3S",
        "KS"
    ]
    "users": [
        {
            "id": "user1",
            "buy_in": 20,
            "balance": 32,
            "bet": 0,
            "fold": 0,
            "hole_cards": [
                "4S",
                "KC"
            ],
            "hand": [
                "KS",
                "QS",
                "TS",
                "8S",
                "4S"
            ],
            "hand_type": "flush",
            "hand_rank": 1,
            "vote": ""
        },
        {
            "id": "user2",
            "buy_in": 20,
            "balance": 16,
            "bet": 0,
            "fold": 0,
            "hole_cards": [
                "JH",
                "3H"
            ],
            "hand": [
                "KS",
                "QS",
                "TS",
                "8S",
                "3S"
            ],
            "hand_type": "flush",
            "hand_rank": 2,
            "vote": ""
        },
        {
            "id": "user3",
            "buy_in": 20,
            "balance": 16,
            "bet": 0,
            "fold": 0,
            "hole_cards": [
                "2D",
                "QC"
            ],
            "hand": [
                "KS",
                "QS",
                "TS",
                "8S",
                "3S"
            ],
            "hand_type": "flush",
            "hand_rank": 2,
            "vote": ""
        },
        {
            "id": "user4",
            "buy_in": 20,
            "balance": 16,
            "bet": 0,
            "fold": 0,
            "hole_cards": [
                "TH",
                "AD"
            ],
            "hand": [
                "KS",
                "QS",
                "TS",
                "8S",
                "3S"
            ],
            "hand_type": "flush",
            "hand_rank": 2,
            "vote": ""
        }
    ]
}
```


#### View Debt Information
```
  GET /users/{user_id}/debts/{debt_id}
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `user_id`      | `string` | **Required**. ID of user with debt |
| `debt_id`      | `string` | **Required**. ID of debt to fetch |

Response:
```
{
    "id": "4240f823-1084-4eb0-8321-cba76ebd4ebe",
    "time": "2022-12-23 18:42:51.107388",
    "amount": 4,
    "lobby": "lobby1",
    "sender": "user2",
    "receiver": "user1"
}
```


#### Create New User
```
  POST /users/{user_id}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. Unique ID for new user |


#### Create New Lobby
```
  POST /users/{user_id}/lobbies/{lobby_id}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user creating lobby |
| `lobby_id` | `string` | **Required**. Unique ID for new lobby |


#### Join Existing Lobby
```
  PUT /users/{user_id}/lobbies/{lobby_id}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user joining lobby |
| `lobby_id` | `string` | **Required**. ID of lobby being joined |


#### Buy In
```
  PUT /users/{user_id}/lobbies/{lobby_id}/buy_in/{amount}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user buying in |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |
| `amount` | `integer` | **Required**. Number of chips to buy in |


#### Vote to Play
```
  PUT /users/{user_id}/lobbies/{lobby_id}/votes/play
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user casting vote |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |

#### Vote to Exit
```
  PUT /users/{user_id}/lobbies/{lobby_id}/votes/exit
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user casting vote |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |


#### Call or Check
```
  PUT /users/{user_id}/lobbies/{lobby_id}/actions/call
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user calling or checking |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |

#### Raise
```
  PUT /users/{user_id}/lobbies/{lobby_id}/actions/raise/{amount}
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user raising |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |
| `amount` | `integer` | **Required**. Number of chips to raise |

#### Fold
```
  PUT /users/{user_id}/lobbies/{lobby_id}/actions/fold
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `user_id` | `string` | **Required**. ID of user folding |
| `lobby_id` | `string` | **Required**. ID of lobby user is in |


