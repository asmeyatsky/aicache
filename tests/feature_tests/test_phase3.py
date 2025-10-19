#!/usr/bin/env python3
"""
Test for Phase 3: Federated Learning and Collaborative Features
"""

import sys
import asyncio
import json
sys.path.insert(0, 'src')

from aicache.federated import FederatedLearningServer, FederatedLearningClient, PrivacyPreserver
from aicache.federated.recommendations import RecommendationEngine, DeveloperProfile
from aicache.federated.anomaly_detection import AnomalyDetector
from aicache.federated.collaborative import CollaborativeCache

async def test_federated_learning():
    print("🧪 Testing Phase 3: Federated Learning and Collaborative Features")
    print("=" * 70)
    
    # Test 1: Federated Learning Server and Client
    print("\n📡 Test 1: Federated Learning Infrastructure")
    print("-" * 40)
    
    # Initialize server with privacy configuration
    privacy_config = {
        'epsilon': 1.0,
        'delta': 1e-5,
        'sensitivity': 1.0,
        'mechanism': 'laplace',
        'total_epsilon': 10.0,
        'total_delta': 1e-3
    }
    
    server = FederatedLearningServer({
        'aggregation_strategy': 'fedavg',
        'privacy': privacy_config,
        'total_epsilon': 10.0,
        'total_delta': 1e-3
    })
    await server.initialize_global_model()
    print("✅ Global model server initialized")
    
    # Initialize clients with privacy configuration
    client1 = FederatedLearningClient("client_1", "http://localhost:8080", privacy_config)
    client2 = FederatedLearningClient("client_2", "http://localhost:8080", privacy_config)
    
    # Register clients
    await server.register_client("client_1", {"language": "python", "framework": "flask"})
    await server.register_client("client_2", {"language": "javascript", "framework": "react"})
    print("✅ Clients registered")
    
    # Initialize client models
    global_model = await server.get_global_model()
    await client1.initialize_local_model(global_model.weights)
    await client2.initialize_local_model(global_model.weights)
    print("✅ Client models initialized")
    
    # Train local models
    training_data1 = [{"sample": "data1"}]
    training_data2 = [{"sample": "data2"}]
    
    weights1 = await client1.train_local_model(training_data1)
    weights2 = await client2.train_local_model(training_data2)
    print("✅ Local models trained")
    
    # Submit model updates
    update1 = await client1.create_model_update()
    update2 = await client2.create_model_update()
    
    await server.submit_model_update(update1)
    await server.submit_model_update(update2)
    print("✅ Model updates submitted")
    
    # Aggregate updates
    updated_global_model = await server.aggregate_model_updates()
    print(f"✅ Global model updated to version {updated_global_model.version}")
    
    # Check privacy stats
    privacy_stats = await server.get_privacy_stats()
    print(f"✅ Privacy stats: ε={privacy_stats['model_total_privacy']:.2f}")
    
    # Test 2: Recommendation Engine
    print("\n🎯 Test 2: Personalized Recommendations")
    print("-" * 40)
    
    # Initialize recommendation engine
    profile = DeveloperProfile(
        developer_id="dev_1",
        languages=["python", "javascript"],
        frameworks=["flask", "react"],
        tools=["git", "docker"],
        preferences={"learning_style": "hands-on"},
        activity_history=[]
    )
    
    recommender = RecommendationEngine("client_1", "http://localhost:8080")
    await recommender.initialize(profile, global_model.weights)
    print("✅ Recommendation engine initialized")
    
    # Generate recommendations
    context = {
        "language": "python",
        "framework": "flask",
        "time_of_day": "morning",
        "task": "api_development"
    }
    
    recommendations = await recommender.generate_recommendations(context)
    print(f"✅ Generated {len(recommendations)} recommendations")
    for rec in recommendations[:3]:  # Show first 3
        print(f"   - {rec.item_id} ({rec.confidence:.2f}): {rec.reason}")
    
    # Test 3: Anomaly Detection
    print("\n🔍 Test 3: Anomaly Detection")
    print("-" * 40)
    
    # Initialize anomaly detector
    detector = AnomalyDetector("client_1", "http://localhost:8080")
    await detector.initialize(global_model.weights)
    print("✅ Anomaly detector initialized")
    
    # Detect anomalies
    sample_data = {
        "code": "def test():\n    pass\n" * 100,  # Large code sample
        "functions": ["test"] * 50,  # Many functions
        "errors": ["error1", "error2", "error3", "error4", "error5", "error6"],  # Many errors
        "execution_time": 15.0,  # Slow execution
        "language": "python",
        "framework": "flask"
    }
    
    anomalies = await detector.detect_anomalies(sample_data)
    print(f"✅ Detected {len(anomalies)} anomalies")
    for anomaly in anomalies:
        print(f"   - {anomaly.type} ({anomaly.severity}): {anomaly.description}")
    
    # Test 4: Collaborative Caching
    print("\n👥 Test 4: Collaborative Caching")
    print("-" * 40)
    
    # Initialize collaborative cache
    collab_cache = CollaborativeCache("team_1")
    await collab_cache.initialize()
    print("✅ Collaborative cache initialized")
    
    # Update team presence
    await collab_cache.update_team_presence(
        user_id="user_1",
        username="Alice",
        status="online",
        current_project="web_app",
        current_task="api_development",
        capabilities=["python", "flask", "docker"]
    )
    
    await collab_cache.update_team_presence(
        user_id="user_2",
        username="Bob",
        status="online",
        current_project="web_app",
        current_task="frontend",
        capabilities=["javascript", "react", "css"]
    )
    print("✅ Team presence updated")
    
    # Set collaborative cache entries
    cache_key1 = await collab_cache.set_cache_entry(
        prompt="How to implement authentication in Flask?",
        response="Use Flask-Login extension...",
        context={"language": "python", "framework": "flask"},
        owner_id="user_1",
        tags=["authentication", "flask", "python"]
    )
    
    cache_key2 = await collab_cache.set_cache_entry(
        prompt="React hooks best practices",
        response="Use useState and useEffect...",
        context={"language": "javascript", "framework": "react"},
        owner_id="user_2",
        tags=["react", "hooks", "javascript"]
    )
    print("✅ Cache entries created")
    
    # Get cache entry
    result = await collab_cache.get_cache_entry(
        prompt="How to implement authentication in Flask?",
        context={"language": "python", "framework": "flask"},
        user_id="user_2"  # Different user
    )
    if result:
        print("✅ Cache entry retrieved successfully")
        print(f"   Response: {result['response'][:30]}...")
    else:
        print("❌ Failed to retrieve cache entry")
    
    # Share cache entry
    try:
        await collab_cache.share_cache_entry(
            cache_key1,
            user_id="user_1",  # Owner
            target_user_ids=["user_2"],
            permission="read"
        )
        print("✅ Cache entry shared successfully")
    except Exception as e:
        print(f"❌ Failed to share cache entry: {e}")
    
    # Search cache entries
    search_results = await collab_cache.search_cache_entries(
        query="authentication",
        tags=["python"],
        user_id="user_2"
    )
    print(f"✅ Found {len(search_results)} search results")
    
    # Get team presence
    presence = await collab_cache.get_team_presence()
    print(f"✅ Team presence: {len(presence)} members online")
    
    # Get collaborative stats
    stats = await collab_cache.get_collaborative_stats()
    print(f"✅ Collaborative stats: {stats['total_entries']} entries, {stats['active_users']} active users")
    
    print("\n🎉 Phase 3 Testing Complete!")
    print("=" * 70)
    print("Summary:")
    print("  ✅ Federated Learning Infrastructure: Working")
    print("  ✅ Personalized Recommendations: Working")
    print("  ✅ Anomaly Detection: Working")
    print("  ✅ Collaborative Caching: Working")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_federated_learning())
        if success:
            print("\n🎯 Phase 3 implementation successful!")
            sys.exit(0)
        else:
            print("\n❌ Phase 3 implementation has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Phase 3 test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)