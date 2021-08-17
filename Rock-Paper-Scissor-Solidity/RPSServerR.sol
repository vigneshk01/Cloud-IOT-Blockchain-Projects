// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.6;

contract RPSGame {
    // GameState - INITIATED after inital game setup, RESPONDED after responder adds hash choice, WIN or DRAW after final scoring
    enum RPSGameState {INITIATED, RESPONDED, WIN, DRAW}
    
    // PlayerState - PENDING until they add hashed choice, PLAYED after  madding hash choice, CHOICE_STORED once raw choice and random string are stored
    enum PlayerState {PENDING, PLAYED, CHOICE_STORED}
    
    // 0 before choices are stored, 1 for Rock, 2 for Paper, 3 for Scissors. Strings are stored only to generate comment with choice names
    string[4] choiceMap = ['None', 'Rock', 'Paper', 'Scissors'];
    
    // store the game logic in a mapping
    mapping(uint8 => mapping(uint8 => ResultDetail)) private gameLogic;
    
    // Details of the Game Logic grouped as Struct
    struct ResultDetail {
        address winner;
        string comment;
    }
    
    struct RPSGameData {  
        address initiator; // Address of the initiator
        PlayerState initiator_state; // State of the initiator
        bytes32 initiator_hash; // Hashed choice of the initiator
        uint8 initiator_choice; // Raw number of initiator's choice - 1 for Rock, 2 for Paper, 3 for Scissors
        string initiator_random_str; // Random string chosen by the initiator
        
	    address responder; // Address of the responder
        PlayerState responder_state; // State of the responder
        bytes32 responder_hash; // Hashed choice of the responder
        uint8 responder_choice; // Raw number of responder's choice - 1 for Rock, 2 for Paper, 3 for Scissors
        string responder_random_str; // Random string chosen by the responder
                
        RPSGameState state; // Game State
        address winner; // Address of winner after completion. addresss(0) in case of draw
        string comment; // Comment specifying what happened in the game after completion
    }
    
    RPSGameData _gameData;
    
    // Initiator sets up the game and stores its hashed choice in the creation itself. Game and player states are adjusted accordingly
    constructor(address _initiator, address _responder, bytes32 _initiator_hash) {
        _gameData = RPSGameData({
                                    initiator: _initiator,
                                    initiator_state: PlayerState.PLAYED,
                                    initiator_hash: _initiator_hash, 
                                    initiator_choice: 0,
                                    initiator_random_str: '',
                                    responder: _responder, 
                                    responder_state: PlayerState.PENDING,
                                    responder_hash: 0, 
                                    responder_choice: 0,
                                    responder_random_str: '',
                                    state: RPSGameState.INITIATED,
                                    winner: address(0),
                                    comment: ''
                                    
                            });
                            setGameLogic();
    }
    
    // Initialize the gameLogic mapping with all the Win Possibilities for a result
    function setGameLogic() private {
        
        gameLogic[1][1].winner = address(0);
        gameLogic[1][1].comment = string(abi.encodePacked(choiceMap[1], ' and ', choiceMap[1], ', it is a tie. '));
        gameLogic[1][2].winner = _gameData.responder;
        gameLogic[1][2].comment = string(abi.encodePacked(choiceMap[2], ' beats ', choiceMap[1]));
        gameLogic[1][3].winner = _gameData.initiator;
        gameLogic[1][3].comment = string(abi.encodePacked(choiceMap[1], ' beats ', choiceMap[3]));
        
        gameLogic[2][1].winner = _gameData.initiator;
        gameLogic[2][1].comment = string(abi.encodePacked(choiceMap[2], ' beats ', choiceMap[1]));
        gameLogic[2][2].winner = address(0);
        gameLogic[2][2].comment = string(abi.encodePacked(choiceMap[2], ' and ', choiceMap[2], ', it is a tie. '));
        gameLogic[2][3].winner = _gameData.responder; 
        gameLogic[2][3].comment = string(abi.encodePacked(choiceMap[3], ' beats ', choiceMap[2]));
        
        gameLogic[3][1].winner = _gameData.responder;
        gameLogic[3][1].comment = string(abi.encodePacked(choiceMap[1], ' beats ', choiceMap[3]));
        gameLogic[3][2].winner = _gameData.initiator;
        gameLogic[3][2].comment = string(abi.encodePacked(choiceMap[3], ' beats ', choiceMap[2]));
        gameLogic[3][3].winner = address(0);
        gameLogic[3][3].comment = string(abi.encodePacked(choiceMap[3], ' and ', choiceMap[3], ', it is a tie. '));
    }
    
    // Responder stores their hashed choice. Game and player states are adjusted accordingly.
    function addResponse(bytes32 _responder_hash) public {
        _gameData.responder_hash = _responder_hash;
        _gameData.state = RPSGameState.RESPONDED;
        _gameData.responder_state = PlayerState.PLAYED;
    }
    
    // Initiator adds raw choice number and random string. If responder has already done the same, the game should process the completion execution
    function addInitiatorChoice(uint8 _choice, string memory _randomStr) public returns (bool) {
        require(_gameData.state == RPSGameState.RESPONDED,"Awaiting for opponent to add response");
        _gameData.initiator_choice = _choice;
        _gameData.initiator_random_str = _randomStr;
        _gameData.initiator_state = PlayerState.CHOICE_STORED;
        if (_gameData.responder_state == PlayerState.CHOICE_STORED) {
            __validateAndExecute();
        }
        return true;
    }

    // Responder adds raw choice number and random string. If initiator has already done the same, the game should process the completion execution
    function addResponderChoice(uint8 _choice, string memory _randomStr) public returns (bool) {
        require(_gameData.state == RPSGameState.RESPONDED,"Awaiting for opponent to add response");
        _gameData.responder_choice = _choice;
        _gameData.responder_random_str = _randomStr;
        _gameData.responder_state = PlayerState.CHOICE_STORED;
        if (_gameData.initiator_state == PlayerState.CHOICE_STORED) {
            __validateAndExecute();
        }
        return true;
    }
    
    // Core game logic to check raw choices against stored hashes, and then the actual choice comparison
    // Can be split into multiple functions internally
    function __validateAndExecute() private{
        bytes32 initiatorCalcHash = sha256(abi.encodePacked(choiceMap[_gameData.initiator_choice], '-', _gameData.initiator_random_str));
        bytes32 responderCalcHash = sha256(abi.encodePacked(choiceMap[_gameData.responder_choice], '-', _gameData.responder_random_str));
        bool initiatorAttempt = false;
        bool responderAttempt = false;
        
        if (initiatorCalcHash == _gameData.initiator_hash) {
            initiatorAttempt = true;
        }
        
        if (responderCalcHash == _gameData.responder_hash) {
            responderAttempt = true;
        }
        
        // Add logic to complete the game first based on attempt validation states, and then based on actual game logic if both attempts are validation
        // Comments can be set appropriately like 'Initator attempt invalid', or 'Scissor beats Paper', etc.
        
        if (initiatorAttempt || responderAttempt) {
            if (initiatorAttempt == false) {
                _gameData.state = RPSGameState.WIN;
                _gameData.winner = _gameData.responder;
                _gameData.comment = string(abi.encodePacked('Initator attempt is invalid'));
            } else if(responderAttempt == false){
                _gameData.state = RPSGameState.WIN;
                _gameData.winner = _gameData.initiator;
                _gameData.comment = string(abi.encodePacked('Responder attempt is invalid'));
            }
        }
        
        if (initiatorAttempt == false && responderAttempt == false) {
            _gameData.state = RPSGameState.DRAW;
            _gameData.winner = address(0);
            _gameData.comment = string(abi.encodePacked('Both Initiator and Responder attempts are invalid'));
        }
        
        if (initiatorAttempt == true && responderAttempt == true) {
           if (_gameData.initiator_choice == _gameData.responder_choice) {
               _gameData.winner = gameLogic[_gameData.initiator_choice][_gameData.responder_choice].winner;
               _gameData.state = RPSGameState.DRAW;
               _gameData.comment = gameLogic[_gameData.initiator_choice][_gameData.responder_choice].comment;
           } else {
               _gameData.winner = gameLogic[_gameData.initiator_choice][_gameData.responder_choice].winner;
               _gameData.state = RPSGameState.WIN;
               _gameData.comment = gameLogic[_gameData.initiator_choice][_gameData.responder_choice].comment;
           }
        }
    }

    // Returns the address of the winner, GameState (2 for WIN, 3 for DRAW), and the comment
    function getResult() public view returns (address, RPSGameState, string memory) {
        require(_gameData.state == RPSGameState.DRAW || _gameData.state == RPSGameState.WIN, "Game is in Progress, Please be patient");
        return (_gameData.winner, _gameData.state, _gameData.comment);
    } 
}


contract RPSServer {
    // Mapping for each game instance with the first address being the initiator and internal key aaddress being the responder
    mapping(address => mapping(address => RPSGame)) _gameList;
    
    modifier addressCheck (address addr) {
        if (addr == address(0)) {
            revert("Cannot use Zero Address");
        }else if (msg.sender == addr) {
            revert("Cannot use own address as opponent");
        } else {
        _;
        }
    }
    
    modifier validateChoice (uint8 choice) {
        require(choice >=1 && choice <=3,"invalid choice, please choose a number between 1 & 3");
        _;
    }
    
    // Initiator sets up the game and stores its hashed choice in the creation itself. New game created and appropriate function called    
    function initiateGame(address _responder, bytes32 _initiator_hash) public addressCheck(_responder){
        RPSGame game = new RPSGame(msg.sender, _responder, _initiator_hash);
        _gameList[msg.sender][_responder] = game;
    }

    // Responder stores their hashed choice. Appropriate RPSGame function called   
    function respond(address _initiator, bytes32 _responder_hash) public  addressCheck(_initiator){
        RPSGame game = _gameList[_initiator][msg.sender];
        game.addResponse(_responder_hash);
    }

    // Initiator adds raw choice number and random string. Appropriate RPSGame function called  
    function addInitiatorChoice(address _responder, uint8 _choice, string memory _randomStr) public addressCheck(_responder) validateChoice(_choice) returns (bool) {
        RPSGame game = _gameList[msg.sender][_responder];
        return game.addInitiatorChoice(_choice, _randomStr);
    }

    // Responder adds raw choice number and random string. Appropriate RPSGame function called
    function addResponderChoice(address _initiator, uint8 _choice, string memory _randomStr) public addressCheck(_initiator) validateChoice(_choice) returns (bool) {
        RPSGame game = _gameList[_initiator][msg.sender];
        return game.addResponderChoice(_choice, _randomStr);
    }
    
    // Result details request by the initiator
    function getInitiatorResult(address _responder) public addressCheck(_responder) view returns (address, RPSGame.RPSGameState, string memory) {
        RPSGame game = _gameList[msg.sender][_responder];
        return game.getResult();
    }

    // Result details request by the responder
    function getResponderResult(address _initiator) public addressCheck(_initiator) view returns (address, RPSGame.RPSGameState, string memory) {
        RPSGame game = _gameList[_initiator][msg.sender];
        return game.getResult();
    }
}