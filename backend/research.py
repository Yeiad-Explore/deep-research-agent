"""
Deep Research Tool - CLI Entry Point
Simple command-line tool for deep web research
"""
import asyncio
import argparse
import sys
import logging
from app.agents.graph_builder import run_research
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Deep Research Tool - AI-powered web research"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Research query/question"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=15,
        help="Maximum number of web results (default: 15)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum iterations (default: 3)"
    )

    args = parser.parse_args()

    try:
        print(f"\n🔬 Starting research: {args.query}\n")
        print("=" * 60)

        # Run research
        config = {
            "max_web_results": args.max_results,
            "max_iterations": args.max_iterations
        }

        final_state = await run_research(args.query, config)

        # Display results
        print("\n" + "=" * 60)
        print("📊 RESEARCH RESULTS")
        print("=" * 60)
        print(f"\nQuery: {args.query}\n")
        print("-" * 60)
        print("Answer:\n")
        print(final_state.get("final_response", "No response generated"))
        print("\n" + "-" * 60)
        
        # Display sources
        sources = final_state.get("sources", [])
        if sources:
            print(f"\n📚 Sources ({len(sources)}):\n")
            for i, source in enumerate(sources[:10], 1):  # Show top 10
                print(f"{i}. {source.get('title', 'Unknown')}")
                print(f"   {source.get('url', '')}\n")

        print("=" * 60)
        print("✅ Research completed!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during research: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
