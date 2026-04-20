"""
Patent discovery - snowball via citations + seed list
"""
import asyncio
from .storage import get_patents

# Pre-defined seed patents for Medtronic (cardiac/medical device related)
# These are well-known Medtronic patent families
MEDTRONIC_SEEDS = [
    "US3955174A",   # Pacemaker
    "US4475551A",   # Cardiac stimulator  
    "US5113869A",   # Implantable pacemaker
    "US5314453A",   # Portable stimulator
    "US5443487A",   # Cardiac depolarization
    "US5741314A",   # Medical lead
    "US5741315A",   # Electrode
    "US6152955A",  # Cardiac lead
    "US6317611B1", # Cardiac monitoring
    "US6408214B1", # DFBM pacemaker
]

async def discover_patents(company: str, known_patents: list[str] | None = None) -> list[str]:
    """
    Discover patents using snowball method from seed patents.
    Falls back to predefined seeds if no known_patents provided.
    """
    from .fetch import fetch_patent_data
    
    seed_patents = known_patents or MEDTRONIC_SEEDS
    
    discovered = set(seed_patents)
    to_fetch = list(seed_patents)
    fetched = set()
    
    print(f"Starting discovery with {len(seed_patents)} seeds...")
    
    max_iterations = 3
    
    while to_fetch and len(fetched) < max_iterations * 10:
        pn = to_fetch.pop(0)
        if pn in fetched:
            continue
        fetched.add(pn)
        
        try:
            data = fetch_patent_data(pn)
            backward = data.get("backward_citations", [])[:3]
            forward = data.get("forward_citations", [])[:3]
            
            for cited in backward + forward:
                if cited and cited not in discovered:
                    discovered.add(cited)
                    to_fetch.append(cited)
                    
        except Exception as e:
            print(f"Error {pn}: {e}")
    
    print(f"Discovered {len(discovered)} patents")
    return list(discovered)

if __name__ == "__main__":
    import asyncio
    patents = asyncio.run(discover_patents("Medtronic"))
    print(patents[:10])